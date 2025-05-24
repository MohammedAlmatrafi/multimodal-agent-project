from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

from embedder import split_text
from transcriber import transcribe_audio
from youtube_downloader import download_audio, extract_first_youtube_url
from db_model import get_chat_history
import json


# def create_agent(persist_directory="db"):
#     llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
#     vectordb = Chroma(
#         persist_directory=persist_directory, embedding_function=OpenAIEmbeddings()
#     )

#     qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectordb.as_retriever())

#     tools = [
#         Tool(
#             name="VideoQA",
#             func=qa_chain.invoke,
#             description="Useful for answering questions about the YouTube video.",
#         ),
#     ]

#     memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

#     agent = initialize_agent(
#         tools,
#         llm,
#         agent="chat-conversational-react-description",
#         verbose=True,
#         memory=memory,
#     )
#     return agent


def build_youtube_rag_tool(chat_id: str) -> Tool:
    def youtube_rag_tool(object: str) -> str:
        try:
            # Convert the input JSON object string into a dictionary
            input_data = json.loads(object)
            query = input_data["query"]
            db = get_vectorstore_for_chat(chat_id)
            youtube_url = extract_first_youtube_url(input_data["url"])
            print(f"Has youtube link?: {youtube_url is not None}")
            if (
                youtube_url is not None and len(db.get()["ids"]) == 0
            ):  # This limits the number of youtube videos to one
                print(f"Attempting download: {youtube_url}")
                audio_path = download_audio(youtube_url)
                # TODO: check file size then block if >25MB
                print(f"Audio output: {audio_path}")
                print(f"Attempting transcription via Whisper")
                audio_text = transcribe_audio(audio_path)
                with open(f"audio/{chat_id}.txt", "w", encoding="utf-8") as f:
                    f.write(audio_text)
                chunks = split_text(audio_text)
                db.add_texts(chunks)
            if len(db.get()["ids"]) == 0:
                return "I wasn't able to retrieve any specific information about the video you mentioned. If you provide the URL of the video, I can help you."
            else:
                results = db.similarity_search_with_score(query, k=10)
                threshold = 0.5
                return [doc.page_content for doc, score in results if score > threshold]
        except Exception as e:
            return "Sorry some error happened."

    return Tool(
        name="YouTubeRAG",
        func=youtube_rag_tool,
        description="Use this tool to answer a question based on a YouTube video. Input should be a string structured like a json: {{query:<literal user query about the video>, url:<user provided youtube url>}}.",
    )


def create_agent(chat_id: str):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    # vectordb = get_vectorstore_for_chat(chat_id)
    # qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectordb.as_retriever())

    tools = [build_youtube_rag_tool(chat_id)]

    # Load history from DB
    history = get_chat_history(chat_id)
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )
    for msg in history:
        (
            memory.chat_memory.add_user_message(msg["content"])
            if msg["role"] == "user"
            else memory.chat_memory.add_ai_message(msg["content"])
        )

    agent = initialize_agent(
        tools,
        llm,
        agent="chat-conversational-react-description",
        verbose=True,
        memory=memory,
    )
    return agent


def get_vectorstore_for_chat(chat_id: str):
    return Chroma(
        persist_directory=f"db/{chat_id}",
        embedding_function=OpenAIEmbeddings(),
    )
