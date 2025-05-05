import { useEffect, useState } from "react";
import Button from "./button";
import clsx from "clsx";
import ReactTimeAgo from "react-time-ago";
import Logo from "./logo";
import { useNavigate, useParams } from "react-router-dom";

type userChats = {
  chats: { chat_id: string; created_at: string; first_message: string }[];
};

const Sidebar = () => {
  const [userChats, setUserChats] = useState<userChats>();
  const { chatId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserChats = async () => {
      const res = await fetch("http://localhost:8000/user_chats", {
        method: "GET",
        credentials: "include",
      });
      const data = (await res.json()) as userChats;
      return data;
    };
    fetchUserChats().then((data) => {
      if (data.chats) {
        setUserChats(data);
      }
    });
  }, [chatId]);

  return (
    <aside className="w-3/12 max-w-3/12 md:w-2/12 md:max-w-2/12 duration-1000 bg-white rounded-2xl flex flex-col gap-5 items-center py-5 px-3">
      <Logo />
      <h1 className="font-bold">Recent Chats</h1>
      <Button onClick={() => navigate("/new")}>New Chat +</Button>
      <ul className="flex flex-col gap-3 w-full overflow-y-auto p-1">
        {userChats?.chats.map((chat) => (
          <li
            key={chat.chat_id}
            className={clsx(
              "text-xs py-3 px-2 overflow-clip rounded-md bg-zinc-50/50 hover:outline-1 outline-zinc-200 transition-colors relative",
              chat.chat_id === chatId ? "bg-zinc-100" : "cursor-pointer"
            )}
            onClick={() => navigate(`/c/${chat.chat_id}`)}
          >
            <h4 className="absolute right-1 opacity-20 top-1/2 -translate-y-1/2 text-xs">
              <ReactTimeAgo date={new Date(chat.created_at)} timeStyle="mini" />
            </h4>
            <p className="whitespace-nowrap w-full fade-text">
              {chat.first_message}
            </p>
          </li>
        ))}
      </ul>
    </aside>
  );
};
export default Sidebar;
