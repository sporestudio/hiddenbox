import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/login';
import Dashboard from './pages/dashboard';
import ProtectedRoute from './components/ProtectedRoute';

const App: React.FC = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />

    <Route
      path="/dashboard"
      element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      }
    />

    {/* Redirect any unkown route to /login. TODO: change to 404 error page */}
    <Route path="*" element={<Navigate to="/login" replace />} />
  </Routes>
);

export default App;
