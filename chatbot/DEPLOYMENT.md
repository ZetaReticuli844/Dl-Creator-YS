# 🚀 Rasa Chatbot Deployment Guide

This guide covers multiple deployment options for your Driving License Management Chatbot.

## 📋 Prerequisites

- Python 3.10 or higher
- Git
- API credentials (see `config.env.example`)
- Domain name (for production)

## 🏠 Local Development Deployment

### Quick Start
```bash
# 1. Clone and setup
git clone <your-repo>
cd chatbot

# 2. Create virtual environment
python3 -m venv rasa_env
source rasa_env/bin/activate  # On Windows: rasa_env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp config.env.example config.env
# Edit config.env with your API credentials

# 5. Train the model
rasa train

# 6. Start action server (Terminal 1)
rasa run actions

# 7. Start Rasa server (Terminal 2)
rasa run
```

### Test Your Chatbot
```bash
# Interactive testing
rasa shell

# API testing
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "test_user", "message": "Hello"}'
```

## 🐳 Docker Deployment

### Prerequisites
- Docker Desktop installed
- Docker Compose

### Deploy with Docker Compose
```bash
# 1. Build and start all services
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f rasa-server

# 4. Stop services
docker-compose down
```

### Services Included
- **Rasa Server**: Port 5005 (Main chatbot API)
- **Action Server**: Port 5055 (Custom actions)
- **PostgreSQL**: Port 5432 (Database)
- **Redis**: Port 6379 (Session storage)
- **MongoDB**: Port 27017 (Alternative database)
- **Nginx**: Port 80/443 (Reverse proxy)
- **Prometheus**: Port 9090 (Monitoring)
- **Grafana**: Port 3000 (Dashboard)

## ☁️ Cloud Deployment Options

### 1. Heroku Deployment

#### Setup
```bash
# 1. Install Heroku CLI
brew install heroku/brew/heroku  # macOS
# or download from https://devcenter.heroku.com/articles/heroku-cli

# 2. Login to Heroku
heroku login

# 3. Create Heroku app
heroku create your-chatbot-name

# 4. Set environment variables
heroku config:set API_BASE_URL=your_api_url
heroku config:set API_AUTH_TOKEN=your_token

# 5. Deploy
git push heroku main
```

#### Heroku Configuration
- Uses `Procfile` for process management
- Uses `runtime.txt` for Python version
- Automatic scaling available

### 2. AWS Deployment

#### Option A: EC2 Instance
```bash
# 1. Launch EC2 instance (t3.medium recommended)
# 2. SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# 3. Install dependencies
sudo yum update -y
sudo yum install -y python3 python3-pip git docker

# 4. Clone and deploy
git clone <your-repo>
cd chatbot
pip3 install -r requirements.txt
rasa train

# 5. Start services
sudo systemctl enable rasa-actions
sudo systemctl enable rasa-server
```

#### Option B: AWS ECS/Fargate
```bash
# 1. Build and push Docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker build -t rasa-chatbot .
docker tag rasa-chatbot:latest your-account.dkr.ecr.us-east-1.amazonaws.com/rasa-chatbot:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/rasa-chatbot:latest

# 2. Deploy using CloudFormation
aws cloudformation create-stack --stack-name rasa-chatbot --template-body file://aws-deployment.yml
```

### 3. Google Cloud Platform

#### Option A: App Engine
```bash
# 1. Install Google Cloud SDK
# 2. Initialize project
gcloud init

# 3. Deploy to App Engine
gcloud app deploy app.yaml
```

#### Option B: GKE (Kubernetes)
```bash
# 1. Create GKE cluster
gcloud container clusters create rasa-cluster --num-nodes=3

# 2. Deploy using kubectl
kubectl apply -f gcp-deployment.yaml

# 3. Get external IP
kubectl get service rasa-chatbot-service
```

### 4. Azure Deployment

#### Option A: App Service
```bash
# 1. Install Azure CLI
# 2. Login to Azure
az login

# 3. Create resource group
az group create --name rasa-chatbot-rg --location eastus

# 4. Deploy using ARM template
az deployment group create --resource-group rasa-chatbot-rg --template-file azure-deployment.json
```

#### Option B: AKS (Kubernetes)
```bash
# 1. Create AKS cluster
az aks create --resource-group rasa-chatbot-rg --name rasa-cluster --node-count 3

# 2. Deploy to AKS
kubectl apply -f gcp-deployment.yaml
```

## 🔧 Production Configuration

### Environment Variables
```bash
# Required for production
export API_BASE_URL=https://your-api-domain.com
export API_AUTH_TOKEN=your_secure_token
export RASA_TOKEN=your_rasa_token
export POSTGRES_USER=rasa_user
export POSTGRES_PASSWORD=secure_password
export MONGO_USER=rasa_user
export MONGO_PASSWORD=secure_password
export GRAFANA_PASSWORD=admin_password
```

### SSL/TLS Configuration
```bash
# For Nginx SSL
sudo certbot --nginx -d your-domain.com

# For Docker with SSL
docker run -p 443:443 -v /etc/letsencrypt:/etc/letsencrypt your-image
```

### Monitoring Setup
```bash
# Access monitoring dashboards
# Prometheus: http://your-domain:9090
# Grafana: http://your-domain:3000 (admin/admin)

# Set up alerts
# Configure alertmanager for notifications
```

## 📊 Performance Optimization

### Scaling Options
1. **Horizontal Scaling**: Multiple Rasa instances behind load balancer
2. **Vertical Scaling**: Increase CPU/memory for single instance
3. **Database Scaling**: Use managed databases (RDS, Cloud SQL)
4. **Caching**: Redis for session storage and response caching

### Recommended Resources
- **Development**: 2 CPU, 4GB RAM
- **Production**: 4 CPU, 8GB RAM minimum
- **High Traffic**: 8+ CPU, 16GB+ RAM

## 🔒 Security Best Practices

### Network Security
- Use VPC/private subnets
- Configure security groups/firewall rules
- Enable SSL/TLS encryption
- Use API keys and tokens

### Data Security
- Encrypt data at rest
- Use secure environment variables
- Implement rate limiting
- Regular security updates

### Access Control
- Use IAM roles and policies
- Implement authentication
- Audit logging
- Regular access reviews

## 🚨 Troubleshooting

### Common Issues

#### 1. Model Training Fails
```bash
# Check training data
rasa data validate

# Debug training
rasa train --debug
```

#### 2. Action Server Not Responding
```bash
# Check action server logs
docker-compose logs action-server

# Test action endpoint
curl http://localhost:5055/health
```

#### 3. API Integration Issues
```bash
# Test API connectivity
python test_api_integration.py

# Check environment variables
echo $API_BASE_URL
echo $API_AUTH_TOKEN
```

#### 4. Memory Issues
```bash
# Monitor resource usage
docker stats

# Increase memory limits in docker-compose.yml
```

### Log Analysis
```bash
# View Rasa logs
docker-compose logs rasa-server

# View action server logs
docker-compose logs action-server

# Monitor in real-time
docker-compose logs -f
```

## 📈 Monitoring and Analytics

### Key Metrics to Monitor
- Response time
- Error rates
- User satisfaction
- Conversation success rates
- API call performance

### Alerting Setup
```bash
# Configure Prometheus alerts
# Set up Grafana dashboards
# Configure email/Slack notifications
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy Chatbot
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to production
      run: |
        # Your deployment commands
```

## 📞 Support

For deployment issues:
1. Check logs and error messages
2. Verify environment configuration
3. Test API connectivity
4. Review security group settings
5. Contact support with detailed error information

---

**Happy Deploying! 🚀**




