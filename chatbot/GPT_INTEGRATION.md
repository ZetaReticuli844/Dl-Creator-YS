# DeepSeek Integration for Rasa Chatbot

This document explains how to use the DeepSeek AI integration with your driving license management chatbot.

## Overview

The chatbot now includes DeepSeek-powered AI assistance while maintaining all its existing functionality for driving license management. The integration provides:

1. **Fallback Support**: When Rasa doesn't understand a query, DeepSeek provides a helpful response
2. **General Questions**: Users can ask general questions and get AI-powered answers
3. **Enhanced User Experience**: More natural conversations while preserving license management features

## Setup Instructions

### 1. Environment Configuration

Add your DeepSeek API key to the `.env` file:

```bash
# DeepSeek Configuration
DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
```

### 2. Install Dependencies

The required dependencies are already added to `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Test the Integration

Run the test script to verify everything is working:

```bash
python test_gpt_integration.py
```

## How It Works

### Original Functionality (Preserved)

All existing chatbot features continue to work exactly as before:

- ✅ Check license status
- ✅ View license information  
- ✅ License renewals
- ✅ Duplicate license requests
- ✅ Add/remove vehicle types
- ✅ Address and contact updates
- ✅ License status updates
- ✅ All existing workflows and responses

### New GPT Features

#### 1. Smart Fallback
When users ask something the chatbot doesn't understand:

**User**: "What's the process for getting a motorcycle endorsement?"
**Bot**: *Uses GPT to provide helpful information while staying in context*

#### 2. Direct AI Queries
Users can explicitly ask for AI assistance:

**User**: "Ask AI: What are the traffic rules for new drivers?"
**Bot**: *GPT provides comprehensive answer + reminds about license services*

#### 3. General Questions
Users can ask non-license questions:

**User**: "What's the weather like?"
**Bot**: *GPT responds helpfully while steering back to license services*

## Usage Examples

### License Management (Original Functionality)
```
User: "Check my license status"
Bot: ✅ Great news! Your license is currently ACTIVE and valid until 2025-12-31...

User: "I need to renew my license"
Bot: 🔄 Your license renewal has been initiated! You'll receive a confirmation email...
```

### GPT-Enhanced Interactions
```
User: "What documents do I need for a license?"
Bot: [GPT provides detailed document requirements while staying in license context]

User: "Ask AI about safe driving tips"
Bot: [GPT provides safety tips] + 💡 Remember, I can also help with license services!

User: "Random gibberish text"
Bot: [GPT provides helpful clarification while offering license assistance]
```

## Configuration Options

### GPT Models
The integration uses `gpt-3.5-turbo` by default. You can modify the model in `actions/actions.py`:

```python
model="gpt-4"  # For more advanced responses
model="gpt-3.5-turbo"  # For faster, cost-effective responses
```

### Response Limits
- **Max tokens**: 300 for fallback, 250 for queries
- **Temperature**: 0.7 for fallback, 0.8 for queries
- **Timeout**: 10 seconds

### Context Awareness
The GPT integration maintains conversation context by:
- Including recent conversation history
- Preserving chatbot identity as a license management assistant
- Steering conversations back to license services when appropriate

## Troubleshooting

### Common Issues

1. **OpenAI API Key Not Found**
   - Ensure your API key is properly set in the `.env` file
   - Restart the action server after updating the key

2. **API Quota Exceeded**
   - Check your OpenAI account billing and usage limits
   - Consider upgrading your OpenAI plan

3. **Import Errors**
   - Run `pip install -r requirements.txt` to install all dependencies
   - Ensure you're using the correct Python environment

4. **GPT Responses Not Working**
   - Check the action server logs for error messages
   - Run the test script to verify connectivity
   - Ensure your internet connection is stable

### Testing Commands

```bash
# Test the integration
python test_gpt_integration.py

# Train the model with new features
rasa train

# Start action server
rasa run actions

# Start chatbot server
rasa run

# Test specific endpoints
rasa shell
```

## Cost Considerations

- GPT integration only activates for fallback scenarios and direct AI requests
- License management functions continue to work without API calls
- Typical usage: ~100-500 tokens per GPT interaction
- Cost: ~$0.001-0.005 per interaction (with GPT-3.5-turbo)

## Security Notes

- API keys are loaded from environment variables (never hardcoded)
- Conversation context is limited to recent messages only
- No sensitive license data is sent to OpenAI
- All existing security measures remain in place

## Customization

You can customize the GPT behavior by modifying the system prompts in `actions/actions.py`:

```python
system_prompt = """Your custom instructions here..."""
```

The integration is designed to be:
- **Non-intrusive**: Doesn't interfere with existing functionality
- **Contextual**: Maintains awareness of the license management purpose
- **Fallback-focused**: Only activates when needed
- **Cost-effective**: Minimizes unnecessary API calls

## Support

If you encounter any issues:
1. Run the test script first: `python test_gpt_integration.py`
2. Check the action server logs for detailed error messages
3. Verify your OpenAI API key and account status
4. Ensure all dependencies are properly installed

The chatbot will continue to function normally even if GPT integration fails, ensuring uninterrupted license management services.
