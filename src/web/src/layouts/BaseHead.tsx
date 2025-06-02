import React, { useEffect } from "react";

interface Props {
  title: string;
  description: string;
}

const BaseHead: React.FC<Props> = ({ title, description }) => {
  const canonicalURL = `${window.location.origin}${window.location.pathname}`;

  useEffect(() => {
    const setTheme = () => {
      const theme = (() => {
        if (typeof localStorage !== "undefined" && localStorage.getItem("theme")) {
          return localStorage.getItem("theme");
        }
        if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
          return "dark";
        }
        return "light";
      })();

      if (theme === "light") {
        document.documentElement.classList.remove("dark");
      } else {
        document.documentElement.classList.add("dark");
      }

      window.localStorage.setItem("theme", theme || "dark");
    };

    setTheme();

    const handleThemeChange = () => setTheme();
    document.addEventListener("astro:after-swap", handleThemeChange);

    return () => {
      document.removeEventListener("astro:after-swap", handleThemeChange);
    };
  }, []);

  return (
    <head>
      {/* Global Metadata */}
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <meta name="generator" content="React" />

      {/* Favicon */}
      <link rel="icon" type="image/svg+xml" href="/favicon.svg" />

      {/* Fonts */}
      <link
        rel="preload"
        href="/fonts/Inter-Regular.woff2"
        as="font"
        type="font/woff2"
        crossOrigin="anonymous"
      />
      <link
        rel="preload"
        href="/fonts/Inter-Bold.woff2"
        as="font"
        type="font/woff2"
        crossOrigin="anonymous"
      />

      {/* Canonical URL */}
      <link rel="canonical" href={canonicalURL} />

      {/* Primary Meta Tags */}
      <title>{title}</title>
      <meta name="title" content={title} />
      <meta name="description" content={description} />
    </head>
  );
};

export default BaseHead;