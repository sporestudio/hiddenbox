import React from "react";

type Props = {
  title: string;
};

const Heading: React.FC<Props> = ({ title }) => {
  return (
    <header className="flex flex-col items-center sm:mt-24">
      <h1 className="mb-6 text-center">{title}</h1>
    </header>
  );
};

export default Heading;