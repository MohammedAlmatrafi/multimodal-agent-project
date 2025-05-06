import clsx from "clsx";
import { motion } from "motion/react";
import { useParams } from "react-router-dom";
import ShinyText from "./shinyText";

export type messageList = { role: string; content: string; id: string }[];

const MessageList = ({
  messages,
  messageListRef,
  waiting,
}: {
  messages: messageList;
  messageListRef: React.RefObject<HTMLUListElement | null>;
  waiting: boolean;
}) => {
  const { chatId } = useParams<{ chatId: string | undefined }>();
  const isNew = chatId === undefined;

  return (
    <motion.ul
      ref={messageListRef}
      className="flex flex-col gap-3 overflow-y-auto  max-w-full text-sm"
    >
      {messages.map((msg, index) => {
        const videoId = extractYouTubeId(msg.content);
        return (
          <motion.li
            key={msg.id}
            initial={{ opacity: 0, left: -10 }}
            animate={{
              opacity: 1,
              left: 0,
              transition: {
                delay:
                  index >= messages.length - 10
                    ? 0.1 * (messages.length - index)
                    : 0.05 * (messages.length - index),
              },
            }}
            className={clsx("rounded-xl p-2 break-words relative", {
              // "bg-zinc-50": msg.role === "user",
              "bg-emerald-800/5": msg.role === "agent",
              hidden: isNew,
            })}
          >
            <h1 className="font-bold">
              {msg.role === "user" ? "Me" : "Agent"}
            </h1>
            <p>{msg.content}</p>
            {videoId && (
              <iframe
                width="100%"
                height="200"
                src={`https://www.youtube.com/embed/${videoId}`}
                title="YouTube Preview"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                className="rounded-lg w-fit"
              />
            )}
          </motion.li>
        );
      })}
      {waiting && <ShinyText speedInMs={2000}>Thinking...</ShinyText>}
    </motion.ul>
  );
};
export default MessageList;

export function extractYouTubeId(url: string): string | null {
  const regex =
    /(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
}
