import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()


def split_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return splitter.split_text(text)


def create_vectorstore(chunks, persist_directory="db"):
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_texts(
        chunks, embedding=embeddings, persist_directory=persist_directory
    )
    vectordb.persist()
    return vectordb


def store_chunks_in_chroma(chunks, chat_id: str):
    collection_name = f"youtube_chat_{chat_id}"
    db = Chroma.from_texts(
        texts=chunks, embedding=OpenAIEmbeddings(), collection_name=collection_name
    )
    return db
