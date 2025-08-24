import React from 'react';
import { Navigate } from 'react-router-dom';

const AuthGuard = ({ children }) => {
  // Check if user is logged in by looking for token in localStorage
  const token = localStorage.getItem('token');
  
  // If user is logged in, redirect to home page
  if (token) {
    return <Navigate to="/" replace />;
  }
  
  // If user is not logged in, show the auth page
  return children;
};

export default AuthGuard;
