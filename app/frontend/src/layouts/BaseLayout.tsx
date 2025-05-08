import React from "react";
import '../index.css';
import { useLocation } from 'react-router-dom';
import Starry from "../components/Starry";
import GridBackground from "../components/GridBackground";
import Header from "../components/Header";
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import BaseHead from "../layouts/BaseHead";

const BaseLayout: React.FC<{ title: string; description: string; children?: React.ReactNode }> = ({
  title,
  description,
  children,
}) => {
  const location = useLocation();

  return (
    <html lang="en">
      <head>
        <BaseHead title={title} description={description} />
      </head>
      <body>
        <GridBackground />
        <Starry
          minSize={0.5}
          maxSize={1.5}
          opacity={0.5}
          particleDensity={100}
          className="fixed h-full w-full"
        />
        <Header />
        <NavBar />
        <main className="z-10">{children}</main>
        {location.pathname !== "/login" && <NavBar />}
        <Footer />
      </body>
    </html>
  );
};

export default BaseLayout;
