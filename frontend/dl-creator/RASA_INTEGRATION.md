# Rasa Chatbot Integration

## Overview
The ChatWidget component is now fully integrated with your Rasa chatbot for intelligent driving license assistance.

## Configuration

### Environment Variables
Create a `.env` file in your project root with:

```bash
# Rasa Chatbot URL (Vite format)
VITE_RASA_URL=http://localhost:5005

# Backend API URL (Vite format)
VITE_API_URL=http://localhost:7500
```

**Note:** In Vite, environment variables must be prefixed with `VITE_` to be accessible in the frontend code.

### JWT Token Storage
The ChatWidget automatically retrieves the JWT token from `localStorage.getItem('jwt')` and sends it with every message to Rasa.

## How It Works

### 1. Message Flow
```
User types message → ChatWidget → Rasa API → Response → Display in chat
```

### 2. Authentication
- JWT token is sent in both `Authorization` header and `metadata.token`
- User ID is generated and stored for session management
- Token is automatically included with every request

### 3. API Endpoint
```
POST ${VITE_RASA_URL}/webhooks/rest/webhook
```

### 4. Request Payload
```json
{
  "sender": "user_1234567890",
  "message": "Check my license status",
  "metadata": {
    "token": "jwt_token_here"
  }
}
```

## Features

### ✅ **Real-time Communication**
- Direct integration with Rasa chatbot
- JWT token authentication
- User session management

### ✅ **Fallback Handling**
- Graceful error handling
- Offline fallback responses
- Connection retry logic

### ✅ **Smart Responses**
- Processes multiple Rasa responses
- Staggered message display
- Typing indicators

### ✅ **Security**
- JWT token in headers and metadata
- Secure API communication
- User session isolation

## Usage

### For Users
1. **Login** to your account
2. **Click** the chat button (bottom-right)
3. **Type** your license-related question
4. **Get** intelligent responses from Rasa

### For Developers
1. **Ensure** Rasa server is running on configured URL
2. **Verify** JWT token is being stored correctly
3. **Test** chat functionality with various queries
4. **Monitor** console for any API errors

## Troubleshooting

### Common Issues

#### Chat Not Responding
- Check if Rasa server is running
- Verify `VITE_RASA_URL` in environment
- Check browser console for errors

#### Authentication Errors
- Ensure user is logged in
- Verify JWT token exists in localStorage
- Check token expiration

#### No Messages Displayed
- Check Rasa webhook configuration
- Verify response format from Rasa
- Check network tab for API calls

### Debug Mode
Enable console logging by checking the browser console for:
- Rasa API requests
- Response data
- Error messages
- Token validation

## Rasa Configuration

### Webhook Setup
Ensure your Rasa server has the webhook configured:

```yaml
# credentials.yml
rest:
  webhook_url: "http://localhost:5005/webhooks/rest/webhook"
```

### CORS Configuration
If experiencing CORS issues, configure Rasa to allow your frontend domain.

## Security Notes

- JWT tokens are stored in localStorage
- Tokens are sent with every chat message
- User sessions are isolated by unique IDs
- All communication is over HTTPS (in production)

## Future Enhancements

- [ ] Message encryption
- [ ] File upload support
- [ ] Voice message support
- [ ] Chat history persistence
- [ ] Multi-language support
