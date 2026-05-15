import React, { useState, useEffect } from 'react';
import { Routes, Route, BrowserRouter, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Layout from './components/Layout.jsx';
import Home from './pages/HomeModern.jsx';
import ScriptPreview from './pages/ScriptPreviewModern.jsx';
import Processing from './pages/ProcessingModern.jsx';
import Result from './pages/ResultModern.jsx';
import Dashboard from './pages/Dashboard.jsx';

const AppModern = () => {
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    localStorage.setItem('theme', newTheme ? 'dark' : 'light');
  };

  return (
    <div className={`min-h-screen ${isDarkMode ? 'dark' : 'light'}`}>
      <BrowserRouter>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          <AnimatePresence mode="wait">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/dashboard" element={
                <Layout>
                  <Dashboard />
                </Layout>
              } />
              <Route path="/create" element={
                <Layout>
                  <Home />
                </Layout>
              } />
              <Route path="/script-preview" element={
                <Layout>
                  <ScriptPreview />
                </Layout>
              } />
              <Route path="/processing" element={
                <Layout>
                  <Processing />
                </Layout>
              } />
              <Route path="/result" element={
                <Layout>
                  <Result />
                </Layout>
              } />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AnimatePresence>
        </div>
      </BrowserRouter>
    </div>
  );
};

export default AppModern;
