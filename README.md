# DL Creator Chatbot Application

A comprehensive driving license creation application with React frontend, Spring Boot backend, and Rasa chatbot integration.

## 🏗️ Architecture

- **Frontend**: React.js with Vite
- **Backend**: Spring Boot with JWT authentication
- **Chatbot**: Rasa with custom actions
- **Database**: H2 (development) / PostgreSQL (production)

## 🚀 Quick Start

### Option 1: Docker (Recommended for Production)

#### Start all services with Docker:
```bash
# Production mode
docker-compose up -d

# Development mode with hot reloading
docker-compose -f docker-compose.dev.yml up -d

# With production services (PostgreSQL, Redis, Nginx)
docker-compose --profile production up -d
```

#### Stop all services:
```bash
docker-compose down
```

### Option 2: Development Mode (Without Docker)

#### Prerequisites:
- Java 11 or higher
- Node.js 16 or higher
- Python 3.8 or higher
- pip3

#### Start all services:
```bash
# Make scripts executable
chmod +x dev-start.sh dev-stop.sh

# Start all services
./dev-start.sh
```

#### Stop all services:
```bash
./dev-stop.sh
```

## 📁 Project Structure

```
assignment/
├── frontend/dl-creator/          # React frontend
├── backend/dl_creator/           # Spring Boot backend
├── chatbot/                      # Rasa chatbot
├── docker-compose.yml           # Production Docker setup
├── docker-compose.dev.yml       # Development Docker setup
├── dev-start.sh                 # Development startup script
├── dev-stop.sh                  # Development stop script
└── README.md                    # This file
```

## 🌐 Service URLs

### Development Mode:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:7500
- **H2 Console**: http://localhost:7500/h2-console
- **Rasa Server**: http://localhost:5005
- **Rasa Action Server**: http://localhost:5055

### Production Mode (with Nginx):
- **Application**: http://localhost (or your domain)
- **Backend API**: http://localhost/api
- **Rasa API**: http://localhost/rasa

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
POSTGRES_USER=dl_user
POSTGRES_PASSWORD=dl_password
POSTGRES_DB=dl_creator

# Rasa
RASA_TOKEN=your_rasa_token

# JWT
SECURITY_JWT_SECRET_KEY=your_jwt_secret
SECURITY_JWT_EXPIRATION_TIME=3600000

# Grafana (optional)
GRAFANA_PASSWORD=admin
```

### Frontend Configuration

The frontend automatically detects the environment and configures API endpoints:
- Development: Uses `localhost` URLs
- Production: Uses relative URLs (proxied through Nginx)

## 🛠️ Development

### Frontend Development
```bash
cd frontend/dl-creator
npm install
npm run dev
```

### Backend Development
```bash
cd backend/dl_creator
./mvnw spring-boot:run
```

### Rasa Development
```bash
cd chatbot
python3 -m venv rasa_env
source rasa_env/bin/activate
pip install -r requirements.txt
rasa train
rasa run actions --port 5055 --cors "*"
# In another terminal:
rasa run --port 5005 --cors "*" --enable-api
```

## 🐳 Docker Commands

### Build and Run
```bash
# Build all images
docker-compose build

# Run in background
docker-compose up -d

# Run with logs
docker-compose up

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v
```

### Individual Services
```bash
# Start only backend
docker-compose up backend

# Start only frontend
docker-compose up frontend

# Start only Rasa
docker-compose up rasa-server action-server
```

### Development with Hot Reloading
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Rebuild and restart
docker-compose -f docker-compose.dev.yml up --build
```

## 📊 Monitoring

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f rasa-server
```

### Health Checks
All services include health checks. Check status with:
```bash
docker-compose ps
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :3000
   
   # Kill the process
   kill -9 <PID>
   ```

2. **Docker build fails**
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

3. **Rasa model not found**
   ```bash
   cd chatbot
   rasa train
   ```

4. **Frontend can't connect to backend**
   - Check if backend is running on port 7500
   - Verify CORS configuration in backend
   - Check network connectivity between containers

### Development Scripts Issues

1. **Scripts not executable**
   ```bash
   chmod +x dev-start.sh dev-stop.sh
   ```

2. **Java not found**
   ```bash
   # Install Java
   # macOS: brew install openjdk@11
   # Ubuntu: sudo apt install openjdk-11-jdk
   ```

3. **Node.js not found**
   ```bash
   # Install Node.js
   # macOS: brew install node
   # Ubuntu: sudo apt install nodejs npm
   ```

## 🚀 Deployment

### Production Deployment
```bash
# Build production images
docker-compose build

# Start with production profile
docker-compose --profile production up -d
```

### Environment-Specific Configurations

1. **Development**: Uses H2 in-memory database
2. **Production**: Uses MySQL with persistent storage
3. **Staging**: Can be configured with different environment variables

## 📝 API Documentation

### Backend API Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/licenses` - Get all licenses
- `POST /api/licenses` - Create new license
- `PUT /api/licenses/{id}` - Update license
- `DELETE /api/licenses/{id}` - Delete license

### Rasa API Endpoints

- `POST /webhooks/rest/webhook` - Send message to chatbot
- `GET /status` - Check Rasa server status
- `POST /model/parse` - Parse user message

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request


