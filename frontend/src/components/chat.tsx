import { useEffect, useRef, useState } from "react";
import SplitText from "./SplitText/SplitText";
import { AnimatePresence } from "motion/react";
import { useParams, useNavigate } from "react-router-dom";
import MessageList, { messageList } from "./MessageList";
import { motion } from "motion/react";
import MicRecorder from "./MicRecorder";
import clsx from "clsx";
import { Loader, Mic, MicOff, Send } from "lucide-react";
import ChatButton from "./ChatButton";

const Chat = () => {
  const [messages, setMessages] = useState<messageList>([]);
  const [recording, setRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [input, setInput] = useState("");
  const [postWaiting, setPostWaiting] = useState(false);
  const [getWaiting, setGetWaiting] = useState(false);
  const messageListRef = useRef<HTMLUListElement>(null);
  const { chatId } = useParams<{ chatId: string | undefined }>();
  const isNew = chatId === undefined;
  const navigate = useNavigate();

  useEffect(() => {
    const container = messageListRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages, chatId]);

  useEffect(() => {
    if (!chatId) return;
    const fetchChatHistory = async () => {
      setGetWaiting(true);
      try {
        const response = await fetch(
          `http://localhost:8000/chat_history/${chatId}`,
          {
            method: "GET",
            credentials: "include",
          }
        );
        setGetWaiting(false);
        if (response.ok) {
          const data = (await response.json()) as {
            chat_id: string;
            history: messageList;
          };
          if (data.history && data.history.length > 0) {
            setMessages(data.history);
          }
        } else {
          console.error("Failed to fetch chat history");
        }
      } catch (error) {
        console.error("Error fetching chat history:", error);
      }
    };
    fetchChatHistory();
  }, [chatId]);

  const handleSubmit = async (msg: string) => {
    const newMessage = msg.trim();
    if (!newMessage || postWaiting) return;

    if (isNew) {
      setMessages([
        {
          role: "user",
          content: newMessage,
          id: Math.floor(10000 + Math.random() * 90000).toString(),
        },
      ]);
    } else {
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "user",
          content: newMessage,
          id: Math.floor(10000 + Math.random() * 90000).toString(),
        },
      ]);
    }

    setPostWaiting(true);
    setInput("");

    let finalChatId = chatId;
    if (!finalChatId) {
      // Call /start to create a new chat and get chat_id
      const res = await fetch("http://localhost:8000/start", {
        method: "GET",
        credentials: "include",
      });
      const data = (await res.json()) as { chat_id: string };
      finalChatId = data.chat_id;
      navigate(`/c/${finalChatId}`);
    }

    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ chat_id: finalChatId, user_message: newMessage }),
    });
    const data = (await response.json()) as { response: string; id: string };
    setMessages((prev) => [
      ...prev,
      {
        role: "agent",
        content: data.response,
        id: data.id, //random 5 digits + response
      },
    ]);
    setPostWaiting(false);
  };
  return (
    <div className="w-9/12 md:w-10/12 duration-1000 bg-white p-5 flex flex-col justify-between rounded-2xl max-w-full">
      <div className="grow flex flex-col justify-between h-1  max-w-full p-3">
        <h1 className="font-bold">Chat History</h1>
        <AnimatePresence mode="wait">
          {isNew && (
            <>
              <motion.div exit={{ opacity: 0 }} className="self-center h-fit">
                <SplitText
                  className="font-bold text-3xl"
                  text="What's on your mind today?"
                  delay={15}
                />
              </motion.div>
              <div />
            </>
          )}
          {!isNew && !getWaiting && (
            <MessageList
              messageListRef={messageListRef}
              messages={messages}
              waiting={postWaiting}
            />
          )}
          {getWaiting && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="w-full h-10 bg-zinc-200 rounded-xl animate-pulse mb-2" />
              <div className="w-full h-16 bg-zinc-200 rounded-xl animate-pulse" />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit(input);
        }}
        className={clsx(
          "flex justify-between items-center border-2  rounded-full py-1 px-1",
          isTranscribing ? "border-blue-600/30" : "border-zinc-700/10"
        )}
      >
        <input
          type="text"
          placeholder={isTranscribing ? "Listening..." : "Ask anything"}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="placeholder-zinc-600/25 outline-0 grow text-xs ml-3"
        />
        <div className="relative">
          <MicRecorder
            hide={!recording}
            setTranscribing={setIsTranscribing}
            submitMsg={handleSubmit}
          />
          <ChatButton
            onClick={() => setRecording((prev) => !prev)}
            type="button"
            className="rounded-tr-none rounded-br-none bg-zinc-100 pr-2 text-zinc-400"
          >
            {recording ? (
              <MicOff className="text-red-400" size={20} />
            ) : (
              <Mic size={20} />
            )}
          </ChatButton>
        </div>
        <ChatButton
          type="submit"
          className="rounded-tl-none rounded-bl-none pl-2"
        >
          {postWaiting ? (
            <Loader
              className="animate-spin"
              style={{ animationDuration: "4s" }}
              size={20}
            />
          ) : (
            <Send size={20} />
          )}
        </ChatButton>
      </form>
    </div>
  );
};
export default Chat;
