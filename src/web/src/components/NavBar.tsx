import React from "react";
import ThemeToggle from "./ThemeToggle";
import { FaGithub } from "react-icons/fa";
import { SITE, LINKS } from "../consts";
import { cn } from "../lib/utils";

const NavBar: React.FC = () => {
  const pathname = window.location.pathname;
  const subpath = pathname.match(/[^/]+/g);

  return (
    <div className="fixed bottom-2 left-1/2 z-50 block h-16 -translate-x-1/2 sm:hidden">
      <div className="container mx-auto">
        <div className="flex items-center gap-4 rounded-full border border-black/25 bg-white/80 px-4 py-2 shadow-lg saturate-200 backdrop-blur-sm dark:border-white/25 dark:bg-black/50">
          {/* Navigation links */}
          <nav className="flex gap-2">
            {LINKS.map((LINK) => (
              <a
                key={LINK.HREF}
                href={LINK.HREF}
                className={cn(
                  "flex items-center justify-center duration-300 hover:transition-colors",
                  pathname === LINK.HREF || "/" + subpath?.[0] === LINK.HREF
                    ? "border-b-2 border-black text-black dark:border-white dark:text-white"
                    : "text-black/80 hover:text-black dark:text-white/80 dark:hover:text-white"
                )}
              >
                {LINK.TEXT}
              </a>
            ))}
          </nav>

          {/* Separator */}
          <div className="h-6 w-0.5 bg-black/25 dark:bg-white/25"></div>

          {/* Action Buttons */}
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
            <ThemeToggle id="navbarThemeToggle" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default NavBar;
