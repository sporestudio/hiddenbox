// src/components/LoginCard.tsx
import React, { useState } from 'react';

export const LoginCard: React.FC<{ onSubmit: (email: string, password: string) => void }> = ({ onSubmit }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(email, password);
  };

  return (
    <section className="w-full max-w-md group flex items-center rounded-lg border border-black/25 bg-white/80 p-6 saturate-200 backdrop-blur-sm transition-all duration-300 ease-in-out hover:scale-[1.02] hover:shadow-lg dark:border-white/25 dark:bg-black/50 dark:hover:shadow-white/10">
      <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
        <h2 className="text-lg font-bold text-black/80 dark:text-white/80">Iniciar sesión</h2>

        <input
          type="email"
          placeholder="Correo electrónico"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="rounded-md border border-black/25 bg-white px-3 py-2 text-sm text-black placeholder-black/50 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-white/25 dark:bg-neutral-800 dark:text-white dark:placeholder-white/50"
          required
        />

        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="rounded-md border border-black/25 bg-white px-3 py-2 text-sm text-black placeholder-black/50 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-white/25 dark:bg-neutral-800 dark:text-white dark:placeholder-white/50"
          required
        />

        <button
          type="submit"
          className="mt-2 rounded-md bg-silver-600 px-4 py-2 text-white transition hover:bg-blue-700 dark:bg-gray-500 dark:hover:bg-blue-400"
        >
          Log in
        </button>
      </form>
    </section>
  );
};
