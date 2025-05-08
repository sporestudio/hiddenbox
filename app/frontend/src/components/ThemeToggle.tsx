import React, { useEffect, useState } from "react";
import { FaSun, FaMoon } from "react-icons/fa";
import { cn } from "../lib/utils";

type Props = {
  id: string;
};

const ThemeToggle: React.FC<Props> = ({ id }) => {
  const [isDark, setIsDark] = useState(true); 

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

    if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
      document.documentElement.classList.add("dark");
      setIsDark(true);
    } else {
      document.documentElement.classList.remove("dark");
      setIsDark(false);
    }
  }, []);

  const handleToggleClick = () => {
    const element = document.documentElement;
    const newIsDark = !isDark;

    if (newIsDark) {
      element.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      element.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }

    setIsDark(newIsDark); 
  };

  return (
    <button
      id={id}
      aria-label="Toggle light and dark theme"
      onClick={handleToggleClick}
      className={cn(
        "flex",
        "size-9 rounded-full p-2 items-center justify-center",
        "text-black/80 dark:text-white/80",
        "bg-transparent hover:bg-black/20 dark:hover:bg-white/20",
        "stroke-current hover:stroke-black hover:dark:stroke-white",
        "border border-black/25 dark:border-white/25",
        "hover:transition-colors duration-300"
      )}
    >
      {isDark ? (
        <FaMoon className="block size-full" />
      ) : (
        <FaSun className="block size-full" /> 
      )}
    </button>
  );
};

export default ThemeToggle;