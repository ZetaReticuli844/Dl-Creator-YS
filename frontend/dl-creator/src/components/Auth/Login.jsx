import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { loginUser } from '../../services/authService';
import   { validateLogin }  from '../../utils/validation';
import './Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
    // Clear error when user starts typing
    if (errors[e.target.name]) {
      setErrors({...errors, [e.target.name]: ''});
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { errors, isValid } = validateLogin(formData);
    
    if (!isValid) {
      setErrors(errors);
      return;
    }

    setIsLoading(true);
    try {
      const response = await loginUser(formData);
      alert('Login successful!');
      // Redirect to home page
      window.location.href = '/';
    } catch (error) {
      setErrors(error.errors || { general: 'Login failed. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>Welcome Back</h1>
          <p>Sign in to your account to continue</p>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          {errors.general && (
            <div className="server-error">{errors.general}</div>
          )}
          
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              className={errors.email ? 'input-error' : ''}
            />
            {errors.email && <div className="error-message">{errors.email}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              className={errors.password ? 'input-error' : ''}
            />
            {errors.password && <div className="error-message">{errors.password}</div>}
          </div>
          
          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
        
        <div className="register-link">
          <span>Don't have an account?</span>
          <Link to="/register">Create one here</Link>
        </div>
        
        <div className="back-home">
          <Link to="/">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;