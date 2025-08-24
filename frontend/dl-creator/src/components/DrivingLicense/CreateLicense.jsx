import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createDrivingLicense, getLicenseDetails } from '../../services/licenseService';
import { validateLicense } from '../../utils/validation';
import './CreateLicense.css';

const CreateLicense = () => {
  const [licenseData, setLicenseData] = useState({
    firstName: '',
    lastName: '',
    vehicleType: '',
    vehicleMake: '',
    address: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [hasExistingLicense, setHasExistingLicense] = useState(false);
  const [isCheckingLicense, setIsCheckingLicense] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    checkExistingLicense();
  }, []);

  const checkExistingLicense = async () => {
    try {
      setIsCheckingLicense(true);
      const response = await getLicenseDetails();
      console.log('License check response:', response); // Debug log
      
      // Check if we have actual license data
      if (response && response.data && Object.keys(response.data).length > 0) {
        console.log('Existing license found:', response.data);
        setHasExistingLicense(true);
      } else {
        console.log('No existing license found');
        setHasExistingLicense(false);
      }
    } catch (error) {
      console.log('License check error:', error); // Debug log
      // If error or no data, user doesn't have a license
      setHasExistingLicense(false);
    } finally {
      setIsCheckingLicense(false);
    }
  };

  const handleChange = (e) => {
    setLicenseData({...licenseData, [e.target.name]: e.target.value});
    // Clear error when user starts typing
    if (errors[e.target.name]) {
      setErrors({...errors, [e.target.name]: ''});
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (hasExistingLicense) {
      alert('You already have a license. You can only create one license per account.');
      return;
    }

    const { errors, isValid } = validateLicense(licenseData);
    
    if (!isValid) {
      setErrors(errors);
      return;
    }

    setIsLoading(true);
    try {
      console.log('Submitting license data:', licenseData); // Debug log
      const response = await createDrivingLicense(licenseData);
      console.log('License creation response:', response); // Debug log
      
      alert('Driving License Created Successfully!');
      
      // Update local state to reflect new license
      setHasExistingLicense(true);
      
      // Redirect to license details after a short delay
      setTimeout(() => {
        window.location.href = '/license-details';
      }, 1000);
      
    } catch (error) {
      console.error('License creation error:', error); // Debug log
      setErrors(error.errors || { general: 'Failed to create license. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  if (isCheckingLicense) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Checking license status...</p>
      </div>
    );
  }

  if (hasExistingLicense) {
    return (
      <div className="existing-license-container">
        <div className="existing-license-card">
          <div className="existing-license-header">
            <h1>License Already Exists</h1>
            <p>You already have a driving license. You can only create one license per account.</p>
          </div>
          
          <div className="existing-license-actions">
            <Link to="/license-details" className="view-license-button">
              View My License
            </Link>
            <Link to="/" className="back-home-button">
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="create-license-container">
      <div className="create-license-card">
        <div className="create-license-header">
          <h1>Create Driving License</h1>
          <p>Fill in your details to create your driving license</p>
        </div>
        
        <form onSubmit={handleSubmit} className="create-license-form">
          {errors.general && (
            <div className="server-error">{errors.general}</div>
          )}
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="firstName">First Name</label>
              <input
                type="text"
                id="firstName"
                name="firstName"
                value={licenseData.firstName}
                onChange={handleChange}
                placeholder="Enter your first name"
                className={errors.firstName ? 'input-error' : ''}
              />
              {errors.firstName && <div className="error-message">{errors.firstName}</div>}
            </div>
            
            <div className="form-group">
              <label htmlFor="lastName">Last Name</label>
              <input
                type="text"
                id="lastName"
                name="lastName"
                value={licenseData.lastName}
                onChange={handleChange}
                placeholder="Enter your last name"
                className={errors.lastName ? 'input-error' : ''}
              />
              {errors.lastName && <div className="error-message">{errors.lastName}</div>}
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="vehicleType">Vehicle Type</label>
              <select
                id="vehicleType"
                name="vehicleType"
                value={licenseData.vehicleType}
                onChange={handleChange}
                className={errors.vehicleType ? 'input-error' : ''}
              >
                <option value="">Select vehicle type</option>
                <option value="Motorcycle">Motorcycle</option>
                <option value="Car">Car</option>
                <option value="Truck">Truck</option>
                <option value="Bus">Bus</option>
              </select>
              {errors.vehicleType && <div className="error-message">{errors.vehicleType}</div>}
            </div>
            
            <div className="form-group">
              <label htmlFor="vehicleMake">Vehicle Make</label>
              <input
                type="text"
                id="vehicleMake"
                name="vehicleMake"
                value={licenseData.vehicleMake}
                onChange={handleChange}
                placeholder="Enter vehicle make"
                className={errors.vehicleMake ? 'input-error' : ''}
              />
              {errors.vehicleMake && <div className="error-message">{errors.vehicleMake}</div>}
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="address">Address</label>
            <textarea
              id="address"
              name="address"
              value={licenseData.address}
              onChange={handleChange}
              placeholder="Enter your full address"
              rows="3"
              className={errors.address ? 'input-error' : ''}
            />
            {errors.address && <div className="error-message">{errors.address}</div>}
          </div>
          
          <button 
            type="submit" 
            className="create-license-button"
            disabled={isLoading}
          >
            {isLoading ? 'Creating License...' : 'Create License'}
          </button>
        </form>
        
        <div className="back-home">
          <Link to="/">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
};

export default CreateLicense;