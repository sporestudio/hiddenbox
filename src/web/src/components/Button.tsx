import React from "react";
import { FaGithub } from "react-icons/fa"; 

type Props = {
  icon: string;
  href: string;
  label: string;
};

const Button: React.FC<Props> = ({ icon, href, label }) => {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex w-fit items-center rounded border border-neutral-300 px-3 py-2 hover:bg-neutral-200 dark:border-neutral-700 dark:hover:bg-neutral-800"
      aria-label={label}
    >
      <span className="text-neutral-600 duration-300 hover:transition-colors group-hover:text-black dark:text-neutral-400 dark:group-hover:text-white">
        <FaGithub name={icon} size={20} />
      </span>
    </a>
  );
};

export default Button;