import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { LoginCard } from '../components/LoginCard';
import Starry from "../components/Starry";
import GridBackground from "../components/GridBackground";
import Header from '../components/Header';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (email: string, password: string) => {
    try {
      await login(email, password);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      console.error('Error de login', err);
    }
  };

  return (
    <div className="relative w-full h-screen">
      <GridBackground />
      <Starry
        minSize={0.5}
        maxSize={1.5}
        opacity={0.5}
        particleDensity={100}
        className="fixed h-full w-full"
      />
      <Header />
      <main className="z-10 flex items-center justify-center h-full">
        <LoginCard onSubmit={handleSubmit} />
      </main>
    </div>
  );
};

export default LoginPage;