# DL Creator - Driving License Management System

A modern, secure, and user-friendly web application for creating and managing driving licenses. Built with React and integrated with an intelligent Rasa chatbot for enhanced user experience.

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure login and registration system
- **License Creation**: Create new driving licenses with comprehensive form validation
- **License Management**: View and manage existing license details
- **Responsive Design**: Modern UI that works on all devices
- **Protected Routes**: Secure access to license management features

### AI-Powered Chatbot
- **Rasa Integration**: Intelligent chatbot for license-related queries
- **Real-time Communication**: Instant responses to user questions
- **JWT Authentication**: Secure chat sessions with user authentication
- **Smart Fallbacks**: Graceful error handling and offline support

### Security Features
- **JWT Token Management**: Secure authentication and session management
- **Protected Routes**: Role-based access control
- **Input Validation**: Comprehensive form validation and sanitization
- **Secure API Communication**: HTTPS-ready with proper headers

## 🛠️ Tech Stack

- **Frontend**: React 19.1.1 with Vite
- **Routing**: React Router DOM 7.8.1
- **HTTP Client**: Axios 1.11.0
- **Styling**: CSS3 with modern design patterns
- **AI Chatbot**: Rasa integration
- **Build Tool**: Vite 7.1.2
- **Linting**: ESLint with React-specific rules
- **Containerization**: Docker with multi-stage builds

## 📋 Prerequisites

Before running this project, make sure you have:

- **Node.js** (version 16 or higher)
- **npm** or **yarn** package manager
- **Docker** and **Docker Compose** (for containerized deployment)
- **Rasa Server** running (for chatbot functionality)
- **Backend API** running (for license management)

## 🚀 Installation & Deployment

### Option 1: Traditional Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dl-creator
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment Configuration**
   Create a `.env` file in the project root:
   ```bash
   # Rasa Chatbot URL
   VITE_RASA_URL=http://localhost:5005
   
   # Backend API URL
   VITE_API_URL=http://localhost:7500
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:5173` (or the URL shown in your terminal)

### Option 2: Docker Deployment (Recommended)

#### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dl-creator
   ```

2. **Build and run with Docker Compose**
   ```bash
   # For development
   ./scripts/docker-build.sh dev
   
   # For production
   ./scripts/docker-build.sh prod
   ```

3. **Access the application**
   - Development: `http://localhost:5173`
   - Production: `http://localhost:3000`

#### Manual Docker Commands

**Development Environment:**
```bash
# Build development image
docker build -f Dockerfile.dev -t dl-creator:dev .

# Run with docker-compose
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Production Environment:**
```bash
# Build production image
docker build -t dl-creator:latest .

# Run with docker-compose
docker-compose up -d
```

#### Docker Scripts

Use the provided shell script for easy management:

```bash
# Make script executable (first time only)
chmod +x scripts/docker-build.sh

# Available commands
./scripts/docker-build.sh build-prod    # Build production image
./scripts/docker-build.sh build-dev     # Build development image
./scripts/docker-build.sh dev           # Start development environment
./scripts/docker-build.sh prod          # Start production environment
./scripts/docker-build.sh stop          # Stop all containers
./scripts/docker-build.sh logs          # Show container logs
./scripts/docker-build.sh cleanup       # Clean up Docker resources
./scripts/docker-build.sh help          # Show help
```

## 🐳 Docker Configuration

### Production Setup
- **Multi-stage build** for optimized image size
- **Nginx** for serving static files
- **Health checks** for all services
- **Security headers** and compression enabled

### Development Setup
- **Hot reloading** with volume mounts
- **Development server** with live updates
- **Debug mode** for Rasa chatbot
- **Separate databases** for development

### Services Included
- **Frontend**: React application (port 3000/5173)
- **Backend**: Node.js API (port 7500)
- **Rasa**: Chatbot service (port 5005)
- **Database**: PostgreSQL (port 5432)
- **Redis**: Caching and sessions (port 6379)
- **Nginx Proxy**: Reverse proxy (optional, port 80/443)

## 📁 Project Structure

```
dl-creator/
├── public/                 # Static assets
├── src/
│   ├── components/         # React components
│   │   ├── Auth/          # Authentication components
│   │   ├── ChatWidget/    # AI chatbot integration
│   │   ├── DrivingLicense/ # License management
│   │   ├── Home/          # Landing page
│   │   └── Layout/        # Navigation and layout
│   ├── services/          # API service functions
│   ├── utils/             # Utility functions
│   ├── App.jsx            # Main application component
│   └── main.jsx           # Application entry point
├── scripts/               # Docker and deployment scripts
├── Dockerfile             # Production Docker configuration
├── Dockerfile.dev         # Development Docker configuration
├── docker-compose.yml     # Production services
├── docker-compose.dev.yml # Development services
├── nginx.conf             # Nginx configuration
├── package.json           # Dependencies and scripts
└── vite.config.js         # Vite configuration
```

## 🔧 Available Scripts

### NPM Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build

### Docker Scripts
- `./scripts/docker-build.sh dev` - Start development environment
- `./scripts/docker-build.sh prod` - Start production environment
- `./scripts/docker-build.sh stop` - Stop all containers
- `./scripts/docker-build.sh logs` - Show container logs

## 🎯 Usage

### For End Users

1. **Registration/Login**
   - Visit the homepage
   - Click "Get Started" to register or "Login" to sign in
   - Complete the authentication process

2. **Create License**
   - Navigate to "Create License" after login
   - Fill in the required information:
     - First Name
     - Last Name
     - Vehicle Type
     - Vehicle Make
     - Address
   - Submit the form to create your license

3. **View License Details**
   - Access your license information through the "License Details" page
   - View all license information in a clean, organized format

4. **Chat with AI Assistant**
   - Click the chat button (bottom-right corner)
   - Ask questions about your license, requirements, or general queries
   - Get intelligent responses from the Rasa chatbot

### For Developers

1. **Component Development**
   - All components are modular and reusable
   - Follow the existing patterns for consistency
   - Use the provided CSS files for styling

2. **API Integration**
   - Services are organized in `src/services/`
   - Use the axios configuration in `src/utils/axiosConfig.js`
   - Follow the existing error handling patterns

3. **Authentication**
   - JWT tokens are stored in localStorage
   - Protected routes automatically handle authentication
   - Use the AuthGuard component for login/register pages

4. **Docker Development**
   - Use `docker-compose.dev.yml` for development
   - Hot reloading is enabled with volume mounts
   - Debug mode available for all services

## 🔌 API Integration

### Backend Requirements
The application expects a backend API with the following endpoints:

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/licenses` - Create driving license
- `GET /api/licenses` - Get license details

### Rasa Chatbot Integration
- Webhook endpoint: `POST /webhooks/rest/webhook`
- JWT token authentication
- User session management

## 🚨 Troubleshooting

### Common Issues

**Docker Issues**
- Ensure Docker and Docker Compose are installed
- Check if ports are already in use
- Verify Docker daemon is running

**Chat Not Responding**
- Ensure Rasa server is running on the configured URL
- Check `VITE_RASA_URL` in your environment variables
- Verify network connectivity between containers

**Authentication Errors**
- Clear browser localStorage
- Ensure backend API is running
- Check JWT token expiration

**Build Errors**
- Clear node_modules and reinstall dependencies
- Check Node.js version compatibility
- Verify all environment variables are set

### Debug Mode
Enable console logging to debug issues:
- Check browser console for API requests
- Monitor network tab for failed requests
- Review container logs: `./scripts/docker-build.sh logs`

## 🔒 Security Considerations

- JWT tokens are stored in localStorage (consider httpOnly cookies for production)
- All API communication should use HTTPS in production
- Input validation is implemented on both frontend and backend
- Protected routes prevent unauthorized access
- Docker images use non-root users where possible
- Security headers are configured in Nginx

## 🚀 Deployment

### Docker Deployment

1. **Build the application**
   ```bash
   ./scripts/docker-build.sh build-prod
   ```

2. **Deploy with Docker Compose**
   ```bash
   ./scripts/docker-build.sh prod
   ```

3. **Configure environment variables**
   - Update `.env` file for production values
   - Set up SSL certificates for HTTPS
   - Configure database connections

### Traditional Deployment

1. **Build the application**
   ```bash
   npm run build
   ```

2. **Deploy the `dist` folder**
   - Upload to your web server
   - Configure environment variables for production
   - Ensure HTTPS is enabled

3. **Configure CORS**
   - Update backend CORS settings for your domain
   - Configure Rasa webhook for production URL

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Check the [RASA_INTEGRATION.md](./RASA_INTEGRATION.md) for chatbot setup
- Review the troubleshooting section above
- Open an issue in the repository

---

**Built with ❤️ using React, Vite, and Docker**
