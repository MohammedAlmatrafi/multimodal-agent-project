import clsx from "clsx";

type ChatButtonType = React.ButtonHTMLAttributes<HTMLButtonElement> & {};

const ChatButton = ({ children, className, ...rest }: ChatButtonType) => {
  return (
    <button
      className={clsx(
        "bg-emerald-600 text-white rounded-full p-3 cursor-pointer hover:opacity-90 active:scale-95 flex justify-center items-center aspect-square duration-100",
        className
      )}
      {...rest}
    >
      {children}
    </button>
  );
};
export default ChatButton;
