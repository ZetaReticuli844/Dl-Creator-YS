import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { registerUser } from '../../services/authService';
import { validateRegister } from '../../utils/validation';
import './Register.css';

const Register = () => {
  const [formData, setFormData] = useState({
    fullName: '',
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
    const { errors, isValid } = validateRegister(formData);
    
    if (!isValid) {
      setErrors(errors);
      return;
    }

    setIsLoading(true);
    try {
      const response = await registerUser(formData);
      alert('User registered successfully! Please login.');
      // Redirect to home page
      window.location.href = '/';
    } catch (error) {
      setErrors(error.errors || { general: 'Registration failed. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <div className="register-header">
          <h1>Create Account</h1>
          <p>Join us and create your driving license</p>
        </div>
        
        <form onSubmit={handleSubmit} className="register-form">
          {errors.general && (
            <div className="server-error">{errors.general}</div>
          )}
          
          <div className="form-group">
            <label htmlFor="fullName">Full Name</label>
            <input
              type="text"
              id="fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              placeholder="Enter your full name"
              className={errors.fullName ? 'input-error' : ''}
            />
            {errors.fullName && <div className="error-message">{errors.fullName}</div>}
          </div>
          
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
              placeholder="Create a password"
              className={errors.password ? 'input-error' : ''}
            />
            {errors.password && <div className="error-message">{errors.password}</div>}
          </div>
          
          <button 
            type="submit" 
            className="register-button"
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>
        
        <div className="login-link">
          <span>Already have an account?</span>
          <Link to="/login">Sign in here</Link>
        </div>
        
        <div className="back-home">
          <Link to="/">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;