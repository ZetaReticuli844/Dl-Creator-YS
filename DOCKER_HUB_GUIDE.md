# Docker Hub Setup Guide

This guide explains how to publish your DL Creator application to Docker Hub and use the published images.

## 🚀 Quick Start

### 1. Login to Docker Hub
```bash
docker login
```

### 2. Push Images to Docker Hub
```bash
# Push all images with default settings
./docker-hub-push.sh

# Push with custom username and version
./docker-hub-push.sh --username your-username --version v1.0.0

# Push specific services only
./docker-hub-push.sh frontend backend
```

### 3. Run from Docker Hub
```bash
# Run with default images
docker-compose -f docker-compose.hub.yml up -d

# Run with specific version
DOCKER_USERNAME=your-username VERSION=v1.0.0 docker-compose -f docker-compose.hub.yml up -d
```

## 📋 Prerequisites

1. **Docker Hub Account**: Create an account at [hub.docker.com](https://hub.docker.com)
2. **Docker CLI**: Ensure Docker is installed and running
3. **GitHub Account** (optional): For automated CI/CD

## 🔧 Manual Setup

### Step 1: Login to Docker Hub
```bash
docker login
# Enter your Docker Hub username and password
```

### Step 2: Build and Push Images

#### Option A: Using the Script
```bash
# Make script executable
chmod +x docker-hub-push.sh

# Push all images
./docker-hub-push.sh --username your-username --version v1.0.0
```

#### Option B: Manual Commands
```bash
# Build images
docker build -t your-username/dl-creator-frontend:latest ./frontend/dl-creator
docker build -t your-username/dl-creator-backend:latest ./backend/dl_creator
docker build -t your-username/dl-creator-chatbot:latest ./chatbot

# Push images
docker push your-username/dl-creator-frontend:latest
docker push your-username/dl-creator-backend:latest
docker push your-username/dl-creator-chatbot:latest
```

### Step 3: Create Docker Hub Repository

1. Go to [hub.docker.com](https://hub.docker.com)
2. Click "Create Repository"
3. Create repositories for:
   - `dl-creator-frontend`
   - `dl-creator-backend`
   - `dl-creator-chatbot`

## 🤖 Automated CI/CD with GitHub Actions

### Step 1: Set up GitHub Secrets

In your GitHub repository, go to Settings → Secrets and variables → Actions, and add:

- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token

### Step 2: Create Access Token

1. Go to Docker Hub → Account Settings → Security
2. Click "New Access Token"
3. Give it a name (e.g., "GitHub Actions")
4. Copy the token and add it to GitHub secrets

### Step 3: Push to GitHub

The workflow will automatically:
- Build images on every push to main/develop
- Push images on releases (tags starting with 'v')
- Create GitHub releases

```bash
# Create a release
git tag v1.0.0
git push origin v1.0.0
```

## 📦 Using Published Images

### Option 1: Using docker-compose.hub.yml
```bash
# Set environment variables
export DOCKER_USERNAME=your-username
export VERSION=latest

# Run the application
docker-compose -f docker-compose.hub.yml up -d
```

### Option 2: Using Make Commands
```bash
# Run with default settings
make hub-run

# Run with specific version
make hub-run-version DOCKER_USERNAME=your-username VERSION=v1.0.0
```

### Option 3: Manual Docker Commands
```bash
# Pull images
docker pull your-username/dl-creator-frontend:latest
docker pull your-username/dl-creator-backend:latest
docker pull your-username/dl-creator-chatbot:latest

# Run containers
docker run -d -p 3000:80 your-username/dl-creator-frontend:latest
docker run -d -p 7500:7500 your-username/dl-creator-backend:latest
docker run -d -p 5005:5005 your-username/dl-creator-chatbot:latest
```

## 🏷️ Image Tagging Strategy

### Version Tags
- `latest`: Most recent stable version
- `v1.0.0`: Semantic versioning
- `v1.0`: Major.minor version
- `main-abc123`: Branch-specific builds

### Example Commands
```bash
# Push with version tag
./docker-hub-push.sh --username your-username --version v1.0.0

# Push with custom prefix
./docker-hub-push.sh --username your-username --prefix my-app --version v1.0.0

# Push specific service
./docker-hub-push.sh --username your-username frontend
```

## 🔍 Image URLs

After pushing, your images will be available at:

```
https://hub.docker.com/r/your-username/dl-creator-frontend
https://hub.docker.com/r/your-username/dl-creator-backend
https://hub.docker.com/r/your-username/dl-creator-chatbot
```

## 📊 Monitoring and Management

### View Image Statistics
- Go to your Docker Hub repository
- View pull statistics, tags, and vulnerabilities

### Update Images
```bash
# Update and push new version
./docker-hub-push.sh --username your-username --version v1.0.1

# Update specific service
./docker-hub-push.sh --username your-username --version v1.0.1 frontend
```

### Clean Up Old Images
```bash
# Remove local images
docker rmi your-username/dl-creator-frontend:old-version

# Remove from Docker Hub (via web interface)
# Go to repository → Tags → Delete unwanted tags
```

## 🚀 Production Deployment

### Using Docker Hub Images in Production
```bash
# Create production environment file
cat > .env.prod << EOF
DOCKER_USERNAME=your-username
VERSION=v1.0.0
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=secure_password
RASA_TOKEN=your_rasa_token
EOF

# Deploy with production profile
docker-compose -f docker-compose.hub.yml --env-file .env.prod --profile production up -d
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dl-creator-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dl-creator-frontend
  template:
    metadata:
      labels:
        app: dl-creator-frontend
    spec:
      containers:
      - name: frontend
        image: your-username/dl-creator-frontend:v1.0.0
        ports:
        - containerPort: 80
```

## 🔧 Troubleshooting

### Common Issues

1. **Authentication Failed**
   ```bash
   # Re-login to Docker Hub
   docker logout
   docker login
   ```

2. **Image Push Failed**
   ```bash
   # Check if repository exists
   # Create repository on Docker Hub first
   ```

3. **Permission Denied**
   ```bash
   # Ensure you have write access to the repository
   # Check Docker Hub repository permissions
   ```

4. **Build Context Too Large**
   ```bash
   # Add .dockerignore files to reduce context size
   # Remove unnecessary files from build context
   ```

### Debug Commands
```bash
# Check Docker Hub login status
docker info | grep Username

# List local images
docker images | grep dl-creator

# Check image details
docker inspect your-username/dl-creator-frontend:latest

# View build logs
docker build --progress=plain -t your-username/dl-creator-frontend:latest ./frontend/dl-creator
```

## 📝 Best Practices

1. **Use Semantic Versioning**: Tag releases with `v1.0.0` format
2. **Keep Images Updated**: Regularly update base images and dependencies
3. **Scan for Vulnerabilities**: Use Docker Hub's built-in security scanning
4. **Document Changes**: Update README with each release
5. **Test Before Pushing**: Ensure images work locally before pushing
6. **Use Multi-stage Builds**: Keep production images small
7. **Set Resource Limits**: Configure memory and CPU limits in production

## 🎯 Next Steps

1. **Set up automated builds** with GitHub Actions
2. **Configure security scanning** in Docker Hub
3. **Set up monitoring** for your deployed applications
4. **Create deployment pipelines** for different environments
5. **Document your API** and usage examples

---

**Happy Deploying! 🚀**
