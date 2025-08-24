import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { logout } from '../../services/authService';
import './Navbar.css';

const Navbar = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Check login status on component mount and route change
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (token) {
      setIsLoggedIn(true);
      setUsername(user?.fullName || 'User');
    } else {
      setIsLoggedIn(false);
    }
  }, [location]);

  const handleLogout = () => {
    logout();
    setIsLoggedIn(false);
    navigate('/login');
  };

  const navLinks = [
    { 
      name: 'Home', 
      path: '/', 
      requireAuth: false 
    },
    { 
      name: 'Create License', 
      path: '/create-license', 
      requireAuth: true 
    },
    { 
      name: 'License Details', 
      path: '/license-details', 
      requireAuth: true 
    }
  ];

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="navbar-logo">
          Driving License Portal
        </Link>
      </div>

      <div className="navbar-menu">
        {navLinks
          .filter(link => !link.requireAuth || isLoggedIn)
          .map((link) => (
            <Link 
              key={link.path} 
              to={link.path} 
              className={`navbar-item ${location.pathname === link.path ? 'active' : ''}`}
            >
              {link.name}
            </Link>
          ))
        }

        {isLoggedIn ? (
          <div className="navbar-user-section">
            <span className="navbar-username">
              Welcome, {username}
            </span>
            <button 
              className="navbar-logout-btn" 
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="navbar-auth-links">
            <Link to="/login" className="navbar-item">
              Login
            </Link>
            <Link to="/register" className="navbar-item register-btn">
              Register
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;