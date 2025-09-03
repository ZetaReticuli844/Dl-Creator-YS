import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import AuthGuard from './components/Auth/AuthGuard';
import Home from './components/Home/Home';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import CreateLicense from './components/DrivingLicense/CreateLicense';
import LicenseDetails from './components/DrivingLicense/LicenseDetails';
import logger from './utils/logger';

function App() {
  useEffect(() => {
    logger.info('Frontend application started', { 
      userAgent: navigator.userAgent,
      url: window.location.href 
    });
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route 
          path="/login" 
          element={
            <AuthGuard>
              <Login />
            </AuthGuard>
          } 
        />
        <Route 
          path="/register" 
          element={
            <AuthGuard>
              <Register />
            </AuthGuard>
          } 
        />
        
        {/* Protected Routes */}
        <Route 
          path="/create-license" 
          element={
            <ProtectedRoute>
              <CreateLicense />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/license-details" 
          element={
            <ProtectedRoute>
              <LicenseDetails />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;