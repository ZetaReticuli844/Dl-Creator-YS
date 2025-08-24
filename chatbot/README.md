# 🚗 Driving License Management Chatbot

A comprehensive AI-powered chatbot built with Rasa for managing driving license operations. This chatbot provides 24/7 assistance for license status checks, information viewing, renewals, and modifications.

## 🎯 **Core Features**

### **License Management Operations**
- ✅ **License Status Checking** - Verify if license is active, expired, or suspended
- 📋 **License Information Display** - View comprehensive license details securely
- 🔄 **License Renewal Processing** - Handle standard and expedited renewals
- 📋 **Duplicate License Requests** - Process replacement license applications
- 🚗 **Vehicle Type Management** - Add/remove vehicle authorizations
- 📍 **Address Updates** - Change registered address information
- 📞 **Contact Updates** - Update phone numbers and email addresses

### **Security & Authentication**
- 🔐 **Multi-factor Authentication** - License number + name verification
- 🛡️ **Data Privacy Protection** - Masked sensitive information display
- 📊 **Session Management** - Secure conversation handling
- 🚫 **Rate Limiting** - Prevent abuse and ensure system stability

### **User Experience**
- 🤖 **24/7 Availability** - Round-the-clock license assistance
- 💬 **Natural Language Processing** - Understand user intent naturally
- 🔄 **Conversation Continuity** - Maintain context across interactions
- 📱 **Multi-platform Support** - Works on web, mobile, and messaging platforms

## 🏗️ **Architecture & Technology Stack**

- **Framework**: Rasa 3.6.15 (Open-source conversational AI)
- **Language**: Python 3.10+
- **NLU Engine**: DIET Classifier with advanced entity extraction
- **Custom Actions**: Python-based business logic implementation with API integration
- **Backend Integration**: RESTful API integration with driving license management system
- **Security**: Bearer token authentication and encrypted data handling
- **Testing**: Comprehensive test coverage with pytest and API integration tests

## 📋 **Prerequisites**

- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)
- Git (for version control)

## 🚀 **Installation & Setup**



### **1. Create Virtual Environment**
```bash
python -m venv rasa_env
source rasa_env/bin/activate  # On Windows: rasa_env\Scripts\activate
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Train the Model**
```bash
rasa train
```

### **4. Start the Action Server**
```bash
rasa run actions
```

### **5. Start the Rasa Server**
```bash
rasa run
```

## 🧪 **Testing the Chatbot**

### **Run Tests**
```bash
rasa test
```

### **Interactive Testing**
```bash
rasa shell
```

### **Test Stories**
```bash
rasa test --stories tests/test_stories.yml
```

### **API Integration Testing**
```bash
# Test API connectivity and endpoints
python test_api_integration.py

# Ensure your API backend is running on localhost:7500
# Set your API_AUTH_TOKEN environment variable
```

## 💬 **Usage Examples**

### **License Status Check**
```
User: "What's my license status?"
Bot: "To check your license status, I'll need your license number. Please provide it now."
User: "ABC123456"
Bot: "License number validated successfully. Please provide your full name for verification."
User: "John Smith"
Bot: "✅ Great news! Your license is currently ACTIVE and valid until 2026-12-31. You're all set to drive!"
```

### **License Information View**
```
User: "Show my license information"
Bot: "To view your license information, I'll need your license number. Please provide it now."
User: "ABC123456"
Bot: "License number validated successfully. Please provide your full name for verification."
User: "John Smith"
Bot: "📋 Here are your license details:
     👤 Name: John Smith
     🔢 License #: AB****56
     🚗 Vehicle Types: Car, Motorcycle
     📅 Issue Date: 2021-01-15
     📅 Expiry Date: 2026-12-31
     📍 Address: 123 Main Street, New York, NY 10001
     📞 Contact: john.smith@email.com"
```

### **License Renewal**
```
User: "I need to renew my license"
Bot: "To process your license renewal, I'll need your license number. Please provide it now."
User: "ABC123456"
Bot: "License number validated successfully. Please provide your full name for verification."
User: "John Smith"
Bot: "What type of renewal would you like?
     1️⃣ Standard Renewal (5-7 business days)
     2️⃣ Expedited Renewal (2-3 business days)
     Please choose an option."
User: "Standard renewal"
Bot: "🔄 Your license renewal has been initiated! Renewal ID: A1B2C3D4
     You'll receive a confirmation email with payment instructions. 
     The new license will be mailed to your registered address."
```

## 🔧 **Configuration**

### **API Integration**
The chatbot integrates with your driving license API backend. See `API_INTEGRATION.md` for detailed configuration.

### **Environment Variables**
Create a `.env` file in the root directory:
```env
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

### **Custom Actions Configuration**
The chatbot uses custom actions for business logic. Configure them in `endpoints.yml`:
```yaml
action_endpoint:
  url: "http://localhost:5055/webhook"
```

## 📊 **Training Data Structure**

### **Intents**
- **Core License Operations**: `check_license_status`, `view_license_info`, `renew_license`
- **Modification Operations**: `update_license_info`, `add_vehicle_type`, `change_address`
- **Authentication**: `provide_license_number`, `provide_name`
- **General**: `greet`, `help`, `goodbye`, `thank`

### **Entities**
- `license_number`: User's license identifier
- `full_name`: User's full name
- `vehicle_type`: Type of vehicle authorization
- `new_address`: Updated address information
- `renewal_type`: Type of renewal service

### **Stories**
Comprehensive conversation flows covering all use cases with proper authentication and validation steps.

## 🧪 **Testing Strategy**

### **Unit Tests**
- Custom action testing
- Entity extraction validation
- Intent classification accuracy

### **Integration Tests**
- End-to-end conversation flows
- API integration testing
- Database operation testing

### **Performance Tests**
- Response time measurement
- Concurrent user handling
- Memory usage optimization

## 🔒 **Security Features**

### **Data Protection**
- License number masking in responses
- Encrypted data storage
- Secure session management
- Rate limiting and abuse prevention

### **Authentication**
- Multi-factor verification
- Session timeout management
- Secure token handling
- Audit logging

## 📈 **Monitoring & Analytics**

### **Metrics Tracked**
- Conversation success rates
- User satisfaction scores
- Response time performance
- Error rate monitoring
- Popular query analysis

### **Logging**
- Structured logging with context
- Error tracking and alerting
- Performance metrics collection
- Security event monitoring

## 🚀 **Deployment**

### **Docker Deployment**
```bash
# Build the image
docker build -t license-chatbot .

# Run the container
docker run -p 5005:5005 -p 5055:5055 license-chatbot
```

### **Production Considerations**
- Load balancing for high availability
- Database clustering for scalability
- Monitoring and alerting setup
- Backup and disaster recovery
- SSL/TLS encryption
- Rate limiting and DDoS protection

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### **Development Guidelines**
- Follow PEP 8 coding standards
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

### **Documentation**
- [Rasa Documentation](https://rasa.com/docs/)
- [Custom Actions Guide](https://rasa.com/docs/rasa/custom-actions)
- [Testing Guide](https://rasa.com/docs/rasa/testing-your-assistant)

### **Community Support**
- [Rasa Community Forum](https://forum.rasa.com/)
- [GitHub Issues](https://github.com/rasa/rasa/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/rasa)

### **Contact**
For project-specific support or questions:
- Email: support@license-chatbot.com
- Documentation: https://docs.license-chatbot.com
- Issues: https://github.com/your-org/license-chatbot/issues

## 🔮 **Future Enhancements**

### **Planned Features**
- Multi-language support
- Voice interface integration
- Advanced analytics dashboard
- Machine learning model improvements
- Integration with government databases
- Mobile app development

### **Technology Upgrades**
- Rasa 4.0 migration
- Advanced NLP models
- Real-time database integration
- Cloud-native deployment
- Microservices architecture

---

**Built with ❤️ using Rasa and Python**
