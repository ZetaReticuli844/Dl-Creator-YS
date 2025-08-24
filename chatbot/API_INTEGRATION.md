# 🚗 Driving License API Integration

This document explains how the Rasa chatbot integrates with your driving license API backend.

## 🔗 **API Endpoints**

The chatbot integrates with the following API endpoints:

### **Core Endpoints**
- `POST /drivingLicense/create` - Create new driving license
- `GET /drivingLicense/getLicenseDetails` - Retrieve license information

### **Planned Endpoints** (to be implemented)
- `POST /drivingLicense/update` - Update license information
- `POST /drivingLicense/renew` - Process license renewal
- `POST /drivingLicense/duplicate` - Request duplicate license
- `POST /drivingLicense/addVehicleType` - Add vehicle type authorization
- `POST /drivingLicense/removeVehicleType` - Remove vehicle type authorization
- `POST /drivingLicense/updateAddress` - Update license address
- `POST /drivingLicense/updateContact` - Update contact information

## ⚙️ **Configuration**

### **Environment Variables**

Create a `.env` file in your project root with the following variables:

```bash
# API Configuration
API_BASE_URL=http://localhost:7500
API_AUTH_TOKEN=your_actual_token_here

# API Settings
API_TIMEOUT=30
API_MAX_RETRIES=3
API_RETRY_DELAY=1

# Logging
LOG_LEVEL=INFO
```

### **API Configuration File**

The `api_config.py` file contains all API-related configuration and utility functions.

## 🔐 **Authentication**

The chatbot uses Bearer token authentication. You need to:

1. **Set your API token** in the environment variables
2. **Ensure the token has proper permissions** for all endpoints
3. **Keep the token secure** and never commit it to version control

## 📊 **API Response Format**

The chatbot expects API responses in this format:

```json
{
  "success": true,
  "message": "Driving license retrieved successfully",
  "data": {
    "id": 152,
    "userId": 102,
    "licenseNumber": "DL-102-175578760328916906",
    "issueDate": "2025-08-21T14:46:43.290+00:00",
    "expirationDate": "2025-08-21T14:46:43.290+00:00",
    "firstName": "Alex",
    "lastName": "Rogers",
    "vehicleType": "Car",
    "vehicleMake": "Toyota",
    "address": "123 Main St, Springfield, IL"
  }
}
```

## 🚀 **Current Implementation Status**

### **✅ Fully Implemented**
- License validation
- User authentication
- License status checking
- License information display

### **🔄 Partially Implemented** (with placeholders)
- License renewal
- Duplicate license requests
- Vehicle type management
- Address updates
- Contact updates

### **📋 To Be Implemented**
- Actual API endpoints for update operations
- Error handling for failed API calls
- Retry logic for transient failures
- Rate limiting
- API response caching

## 🔧 **Testing the Integration**

### **1. Start Your API Backend**
```bash
# Ensure your backend is running on localhost:7500
```

### **2. Set Environment Variables**
```bash
export API_BASE_URL=http://localhost:7500
export API_AUTH_TOKEN=your_actual_token
```

### **3. Test the Chatbot**
```bash
# Start the action server
rasa run actions

# In another terminal, start Rasa
rasa run

# Test with sample license numbers from your API
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **API Connection Failed**
   - Check if your backend is running
   - Verify the API_BASE_URL is correct
   - Check firewall/network settings

2. **Authentication Failed**
   - Verify your API_AUTH_TOKEN is correct
   - Check token permissions
   - Ensure token hasn't expired

3. **License Not Found**
   - Verify license numbers exist in your database
   - Check API endpoint parameters
   - Review API response format

### **Debug Mode**

Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## 🔮 **Future Enhancements**

1. **Real-time Updates** - WebSocket integration for live status updates
2. **Payment Integration** - Direct payment processing for renewals
3. **Document Upload** - Handle document submissions
4. **Multi-language Support** - Internationalization
5. **Analytics Dashboard** - Usage statistics and insights

## 📞 **Support**

If you encounter issues:

1. Check the logs for error messages
2. Verify API endpoint accessibility
3. Test API endpoints directly (e.g., with Postman)
4. Review the API documentation
5. Contact your backend development team

## 🔄 **Migration from Simulated Data**

The chatbot has been updated from using simulated data to real API calls. The changes include:

- Replaced hardcoded license data with API calls
- Added proper error handling for API failures
- Implemented real authentication flow
- Added configuration management
- Improved logging and debugging

All existing functionality remains the same from the user's perspective, but now uses real data from your API backend.
