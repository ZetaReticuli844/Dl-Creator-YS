import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { getLicenseDetails } from '../../services/licenseService';
import ChatWidget from '../ChatWidget/ChatWidget';
import './Home.css';

const Home = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [hasLicense, setHasLicense] = useState(false);
  const [isCheckingLicense, setIsCheckingLicense] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
    
    // If logged in, check if user has a license
    if (token) {
      checkLicenseStatus();
    }
  }, []);

  // Refresh license status when component comes into focus
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token && location.pathname === '/') {
      // Add a small delay to ensure any recent changes are reflected
      const timer = setTimeout(() => {
        checkLicenseStatus();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [location.pathname]);

  const checkLicenseStatus = async () => {
    setIsCheckingLicense(true);
    try {
      const response = await getLicenseDetails();
      console.log('Home: License check response:', response); // Debug log
      
      // Check if we have actual license data
      if (response && response.data && Object.keys(response.data).length > 0) {
        console.log('Home: Existing license found:', response.data);
        setHasLicense(true);
      } else {
        console.log('Home: No existing license found');
        setHasLicense(false);
      }
    } catch (error) {
      console.log('Home: License check error:', error); // Debug log
      // If error or no data, user doesn't have a license
      setHasLicense(false);
    } finally {
      setIsCheckingLicense(false);
    }
  };

  const handleLogout = () => {
    // Remove token and user data
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // Update state
    setIsLoggedIn(false);
    setHasLicense(false);
    
    // Redirect to home page
    navigate('/');
  };

  return (
    <div className="home-container">
      {/* Header with logout button */}
      {isLoggedIn && (
        <div className="header">
          <div className="header-content">
            <div className="user-info">
              <span>Welcome back!</span>
            </div>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      )}

      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Driving License Creator</h1>
          <p className="hero-subtitle">
            Create and manage your driving license with ease. 
            A secure and user-friendly platform for all your license needs.
          </p>
          
          {!isLoggedIn ? (
            <div className="cta-buttons">
              <Link to="/register" className="cta-button primary">
                Get Started
              </Link>
              <Link to="/login" className="cta-button secondary">
                Sign In
              </Link>
            </div>
          ) : (
            <div className="cta-buttons">
              {!hasLicense ? (
                <Link to="/create-license" className="cta-button primary">
                  Create License
                </Link>
              ) : (
                <Link to="/license-details" className="cta-button primary">
                  View License
                </Link>
              )}
              
              {hasLicense && (
                <div className="license-status">
                  <span className="status-badge">✓ License Created</span>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="hero-image">
          <div className="license-card-mockup">
            <div className="card-header">
              <div className="card-title">DRIVING LICENSE</div>
              <div className="card-subtitle">Republic of India</div>
            </div>
            <div className="card-content">
              <div className="card-field">
                <span className="field-label">Name:</span>
                <span className="field-value">John Doe</span>
              </div>
              <div className="card-field">
                <span className="field-label">License No:</span>
                <span className="field-value">DL-123456789</span>
              </div>
              <div className="card-field">
                <span className="field-label">Valid Until:</span>
                <span className="field-value">2030-12-31</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="features-section">
        <h2>Why Choose Our Platform?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3>Secure</h3>
            <p>Your data is protected with industry-standard security measures</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Fast</h3>
            <p>Create and manage licenses in minutes, not hours</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📱</div>
            <h3>Responsive</h3>
            <p>Works perfectly on all devices and screen sizes</p>
          </div>
        </div>
      </div>

      {/* Chat Widget - Only show when user is logged in */}
      {isLoggedIn && <ChatWidget />}
    </div>
  );
};

export default Home;
