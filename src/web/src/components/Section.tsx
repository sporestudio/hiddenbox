import React from "react";
import { cn } from "../lib/utils";

type Props = {
  className?: string;
  title?: string;
  children?: React.ReactNode;
};

const Section: React.FC<Props> = ({ className, title, children }) => {
  return (
    <section className={cn("flex flex-col gap-2", className)}>
      {title && (
        <div className="flex items-center gap-2">
          <div className="text-base font-bold text-black dark:text-white">
            {title}
          </div>
          <div className="h-0.5 flex-grow bg-black/25 dark:bg-white/25" />
        </div>
      )}
      {children}
    </section>
  );
};

export default Section;
