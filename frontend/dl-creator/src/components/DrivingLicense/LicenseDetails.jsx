import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getLicenseDetails } from '../../services/licenseService';
import './LicenseDetails.css';

const LicenseDetails = () => {
  const [licenseData, setLicenseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchLicenseDetails = async () => {
      try {
        setLoading(true);
        const response = await getLicenseDetails();
        console.log('LicenseDetails: Response:', response); // Debug log
        
        // Check if we actually got license data
        if (response && response.data && Object.keys(response.data).length > 0) {
          console.log('LicenseDetails: License data found:', response.data);
          setLicenseData(response.data);
        } else {
          console.log('LicenseDetails: No license data found');
          setError('No license found. Please create a license first.');
        }
      } catch (err) {
        console.error('LicenseDetails: Error fetching license:', err); // Debug log
        // Handle different error scenarios
        if (err.response?.status === 404) {
          setError('No license found. Please create a license first.');
        } else {
          setError(err.response?.data?.message || 'Failed to fetch license details');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchLicenseDetails();
  }, [navigate]);

  const handlePrintLicense = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading License Details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-card">
          <h2>No License Found</h2>
          <p>{error}</p>
          <div className="error-actions">
            <button onClick={() => navigate('/create-license')} className="create-license-btn">
              Create License
            </button>
            <Link to="/" className="back-home-btn">
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="license-details-container">
      <div className="license-card">
        <div className="license-header">
          <div className="license-title">
            <h1>Driving License</h1>
            <p>Republic of India</p>
          </div>
          <div className="license-logo">🚗</div>
        </div>

        <div className="license-info">
          <div className="license-section">
            <div className="license-field">
              <span className="field-label">Full Name:</span>
              <span className="field-value">
                {licenseData.firstName && licenseData.lastName 
                  ? `${licenseData.firstName} ${licenseData.lastName}`
                  : licenseData.fullName || 'Not specified'
                }
              </span>
            </div>

            <div className="license-field">
              <span className="field-label">License Number:</span>
              <span className="field-value">{licenseData.licenseNumber || 'Not specified'}</span>
            </div>

            <div className="license-field">
              <span className="field-label">Date of Birth:</span>
              <span className="field-value">
                {licenseData.dateOfBirth 
                  ? new Date(licenseData.dateOfBirth).toLocaleDateString()
                  : 'Not specified'
                }
              </span>
            </div>

            <div className="license-field">
              <span className="field-label">Vehicle Type:</span>
              <span className="field-value">{licenseData.vehicleType || 'Not specified'}</span>
            </div>

            <div className="license-field">
              <span className="field-label">Vehicle Make:</span>
              <span className="field-value">{licenseData.vehicleMake || 'Not specified'}</span>
            </div>

            <div className="license-field">
              <span className="field-label">Address:</span>
              <span className="field-value">{licenseData.address || 'Not specified'}</span>
            </div>

            <div className="license-field">
              <span className="field-label">Issue Date:</span>
              <span className="field-value">
                {licenseData.issueDate 
                  ? new Date(licenseData.issueDate).toLocaleDateString()
                  : 'Not specified'
                }
              </span>
            </div>

            <div className="license-field">
              <span className="field-label">Expiry Date:</span>
              <span className="field-value">
                {licenseData.expiryDate 
                  ? new Date(licenseData.expiryDate).toLocaleDateString()
                  : 'Not specified'
                }
              </span>
            </div>
          </div>

          <div className="license-actions">
            <button 
              className="print-button" 
              onClick={handlePrintLicense}
            >
              🖨️ Print License
            </button>
          </div>
        </div>
        
        <div className="back-home">
          <Link to="/">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
};

export default LicenseDetails;