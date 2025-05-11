import React from "react";
import { SITE } from "../consts";

const Footer: React.FC = () => {
  return (
    <footer className="relative mt-auto hidden bg-white dark:bg-black md:block">
      <section className="overflow-hidden border-t border-black/25 py-3 dark:border-white/25">
        <div className="flex h-full items-center justify-center print:hidden">
          <p className="text-center text-sm text-black/80 dark:text-white/80">
            &copy; {new Date().getFullYear()} {SITE.AUTHOR}. All rights reserved.
          </p>
        </div>
      </section>
    </footer>
  );
};

export default Footer;