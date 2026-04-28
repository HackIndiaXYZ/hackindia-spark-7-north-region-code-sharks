import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AnimatePresence } from 'framer-motion';

// Views
import LandingPage from './LandingPage';
import Dashboard from './Dashboard';
import { Activity } from 'lucide-react';

// Configure axios defaults
axios.defaults.withCredentials = true; // Important for session cookies
export const API_BASE = 'http://127.0.0.1:8000';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-medical-blue selection:text-white">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

// Protected Route Wrapper
function ProtectedRoute({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await axios.get(`${API_BASE}/auth/me`);
        if (res.data && res.data.id) {
          setUser(res.data);
        } else {
          navigate('/');
        }
      } catch (err) {
        console.log('Not authenticated', err);
        navigate('/');
      } finally {
        setIsAuthLoading(false);
      }
    };
    checkAuth();
  }, [navigate]);

  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center">
        <Activity className="w-8 h-8 text-medical-blue animate-pulse mb-4" />
        <p className="text-xs font-mono text-slate-500 uppercase tracking-widest">Verifying Clinical Credentials...</p>
      </div>
    );
  }

  if (!user) {
    return null; // Will navigate away in useEffect
  }

  // Clone the child component and pass the user object to it
  return React.cloneElement(children, { user });
}

export default App;
