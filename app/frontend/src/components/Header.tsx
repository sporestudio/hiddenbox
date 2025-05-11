import React, { useEffect } from "react";
import ThemeToggle from "./ThemeToggle";
import { FaGithub } from "react-icons/fa";
import { SITE, LINKS } from "../consts";
import { cn } from "../lib/utils";

const Header: React.FC = () => {
  useEffect(() => {
    const handleScroll = () => {
      const header = document.getElementById("header");
      if (header) {
        if (window.scrollY > 0) {
          header.classList.add("scrolled");
        } else {
          header.classList.remove("scrolled");
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    handleScroll(); // Run on mount to set the initial state

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  return (
    <header
      id="header"
      className="fixed top-0 z-50 hidden h-16 w-full md:block print:hidden"
    >
      <div className="container mx-auto h-full">
        <div className="relative flex h-full items-center justify-between">
          {/* Logo/Title */}
          <a
            href="/"
            className="font-bold uppercase text-black/80 duration-300 hover:text-black hover:transition-colors dark:text-white/80 dark:hover:text-white"
          >
            {SITE.TITLE}
          </a>

          {/* Navigation */}
          <nav className="hidden items-center gap-1 text-sm md:flex">
            {LINKS.map((LINK) => (
              <a
                key={LINK.HREF}
                href={LINK.HREF}
                className={cn(
                  "flex h-8 items-center justify-center rounded-full px-3 duration-300 hover:transition-colors",
                  window.location.pathname === LINK.HREF ||
                    "/" + window.location.pathname.split("/")[1] === LINK.HREF
                    ? "bg-black text-white dark:bg-white dark:text-black"
                    : "text-black/80 hover:bg-black/20 hover:text-black dark:text-white/80 dark:hover:bg-white/20 dark:hover:text-white"
                )}
              >
                {LINK.TEXT}
              </a>
            ))}
          </nav>

          {/* Icons and Toggles */}
          <div className="flex gap-2">
            <a
              href={SITE.REPO_URL}
              aria-label="Github repository link"
              target="_blank"
              rel="noopener noreferrer"
              className="flex size-9 items-center justify-center rounded-full border border-black/25 p-2 text-black/80 duration-300 hover:bg-black/20 hover:transition-colors dark:border-white/25 dark:text-white/80 dark:hover:bg-white/20"
            >
              <FaGithub name="github" className="block size-full" />
            </a>
            <ThemeToggle id="headerThemeToggle" />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;