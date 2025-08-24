# DL Creator Application Setup Guide

This guide explains how to set up and run your DL Creator chatbot application with both Docker and non-Docker options.

## 🚀 Quick Start Options

### Option 1: Interactive Quick Start (Recommended)
```bash
./quick-start.sh
```
This provides an interactive menu with all options.

### Option 2: Docker Commands
```bash
# Production mode
docker-compose up -d

# Development mode with hot reloading
docker-compose -f docker-compose.dev.yml up -d

# Stop all services
docker-compose down
```

### Option 3: Development Scripts (Without Docker)
```bash
# Start all services
./dev-start.sh

# Stop all services
./dev-stop.sh
```

### Option 4: Make Commands
```bash
# Show all available commands
make help

# Start with Docker
make up

# Start development environment
make start

# Stop all services
make stop
```

## 📁 Files Created

### Docker Configuration
- `docker-compose.yml` - Production Docker setup
- `docker-compose.dev.yml` - Development Docker setup with hot reloading

### Scripts
- `dev-start.sh` - Start all services without Docker
- `dev-stop.sh` - Stop all development services
- `quick-start.sh` - Interactive menu for all options

### Configuration
- `Makefile` - Easy-to-remember commands
- `env.example` - Environment variables template
- `README.md` - Comprehensive documentation

## 🔧 Prerequisites

### For Docker (Option 1 & 2)
- Docker Desktop installed and running
- Docker Compose installed

### For Development Scripts (Option 3)
- Java 11 or higher
- Node.js 16 or higher
- Python 3.8 or higher
- pip3

## 🌐 Service URLs

Once started, your services will be available at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:7500
- **H2 Console**: http://localhost:7500/h2-console
- **Rasa Server**: http://localhost:5005
- **Rasa Action Server**: http://localhost:5055

## 🛠️ Development Workflow

### 1. First Time Setup
```bash
# Install dependencies
make install

# Or use the interactive menu
./quick-start.sh
# Choose option 7: Install dependencies
```

### 2. Daily Development
```bash
# Start development environment
./quick-start.sh
# Choose option 3: Start without Docker (Development)

# Or use the script directly
./dev-start.sh
```

### 3. Production Testing
```bash
# Start production environment
./quick-start.sh
# Choose option 1: Start with Docker (Production)

# Or use Docker directly
docker-compose up -d
```

## 📊 Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Development logs
tail -f logs/backend.log
tail -f logs/frontend.log
```

### Check Status
```bash
# Docker services
docker-compose ps

# Health check
make health

# Interactive status check
./quick-start.sh
# Choose option 6: Check status
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :3000
   
   # Kill the process
   kill -9 <PID>
   ```

2. **Docker Not Running**
   ```bash
   # Start Docker Desktop
   # Then try again
   docker-compose up -d
   ```

3. **Dependencies Missing**
   ```bash
   # Install all dependencies
   make install
   ```

4. **Scripts Not Executable**
   ```bash
   chmod +x *.sh
   ```

### Reset Everything
```bash
# Stop all services
./dev-stop.sh
docker-compose down -v

# Clean Docker
docker system prune -a

# Reinstall dependencies
make install
```

## 🚀 Deployment

### Production Deployment
```bash
# Build and start production services
docker-compose --profile production up -d

# This includes:
# - PostgreSQL database
# - Redis for caching
# - Nginx reverse proxy
```

### Environment Configuration
1. Copy `env.example` to `.env`
2. Update the values as needed
3. Restart services

## 📝 Development Tips

### Hot Reloading
- **Frontend**: Changes are automatically reflected
- **Backend**: Uses Spring Boot DevTools for auto-restart
- **Rasa**: Model changes require retraining

### Database
- **Development**: H2 in-memory database
- **Production**: PostgreSQL with persistent storage

### Debugging
```bash
# View real-time logs
docker-compose logs -f

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec rasa-server bash
```

## 🎯 Recommended Workflow

1. **Development**: Use `./dev-start.sh` for daily development
2. **Testing**: Use `docker-compose up -d` for production-like testing
3. **Deployment**: Use `docker-compose --profile production up -d` for production

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. View the logs for error messages
3. Ensure all prerequisites are installed
4. Try the interactive quick start menu for guided setup

## 🔄 Updates

To update the application:

```bash
# Pull latest changes
git pull

# Rebuild Docker images
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

---


