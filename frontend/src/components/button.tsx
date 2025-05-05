import React from "react";
import { twMerge } from "tailwind-merge";

interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  className?: string;
}

const Button: React.FC<ButtonProps> = ({ onClick, children, className }) => {
  return (
    <button
      onClick={onClick}
      className={twMerge(
        `bg-zinc-100 rounded-xl py-1 px-3 cursor-pointer active:scale-95`,
        className
      )}
    >
      {children}
    </button>
  );
};

export default Button;
