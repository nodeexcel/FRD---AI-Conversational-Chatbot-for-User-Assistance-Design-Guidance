// Main React application
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import DesignPage from './pages/DesignPage';
import SettingsPage from './pages/SettingsPage';
import DocumentsPage from './pages/DocumentsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import TranslationTestPage from './pages/TranslationTestPage';
import VoiceTestPage from './pages/VoiceTestPage';
import { useAuthStore } from './services/authService';
import './index.css';

// Protected Route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, checkAuth } = useAuthStore();
  
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// Public Route wrapper (redirect if already authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, checkAuth } = useAuthStore();
  
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
};

function App() {
  const { checkAuth } = useAuthStore();
  
  // Check auth on app load
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* Public Routes */}
          <Route 
            path="/login" 
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            } 
          />
          <Route 
            path="/signup" 
            element={
              <PublicRoute>
                <SignupPage />
              </PublicRoute>
            } 
          />
          
          {/* Protected Routes */}
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/design" 
            element={
              <ProtectedRoute>
                <DesignPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/documents" 
            element={
              <ProtectedRoute>
                <DocumentsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/analytics" 
            element={
              <ProtectedRoute>
                <AnalyticsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/translate" 
            element={
              <ProtectedRoute>
                <TranslationTestPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/voice" 
            element={
              <ProtectedRoute>
                <VoiceTestPage />
              </ProtectedRoute>
            } 
          />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
