# 🐳 AppointmentHub Docker Deployment Guide

Complete guide for deploying the AppointmentHub application using Docker and Docker Compose.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Deployment Options](#deployment-options)
5. [Development Setup](#development-setup)
6. [Production Deployment](#production-deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)
9. [Security Considerations](#security-considerations)

## 🚀 Prerequisites

### System Requirements
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: Minimum 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### Install Docker (Ubuntu/Debian)
```bash
# Update package index
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

## ⚡ Quick Start

### 1. Clone and Setup
```bash
# Navigate to the project directory
cd appointment-hub

# Copy environment template
cp .env.example .env

# Edit environment variables (important!)
nano .env
```

### 2. Deploy with One Command
```bash
# Run the deployment script
./scripts/deploy.sh deploy
```

### 3. Access Your Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **Database**: localhost:5432

### 4. Test with Demo Accounts
```
Admin: admin@demo.com / password123
Manager: manager@demo.com / password123
Client: client@demo.com / password123
```

## ⚙️ Configuration

### Environment Variables (.env)

Create your `.env` file from the template and configure:

```bash
# Database Configuration
DB_PASSWORD=your_secure_database_password

# Application Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
JWT_SECRET_KEY=your-jwt-secret-key-also-minimum-32-characters

# External API Keys
STRIPE_SECRET_KEY=sk_test_your_actual_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_stripe_publishable_key
CALENDLY_ACCESS_TOKEN=your_calendly_personal_access_token
EASYSMS_API_KEY=your_easysms_api_key

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
```

### Service Configuration

The Docker Compose setup includes:

- **PostgreSQL Database**: Persistent data storage
- **Redis Cache**: Session management and caching
- **Flask Backend**: API server with Gunicorn
- **React Frontend**: Nginx-served React application
- **Nginx Load Balancer**: Optional for production scaling

## 🔧 Deployment Options

### Option 1: Full Production Deployment
```bash
# Complete deployment with all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Development Deployment
```bash
# Use development configuration with hot reload
docker-compose -f docker-compose.dev.yml up -d

# Frontend will be available at http://localhost:3000
# Backend will be available at http://localhost:5001
```

### Option 3: Using Deployment Script
```bash
# Full deployment
./scripts/deploy.sh deploy

# Start services
./scripts/deploy.sh start

# Stop services
./scripts/deploy.sh stop

# View status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs

# View specific service logs
./scripts/deploy.sh logs backend
```

## 🛠️ Development Setup

### Hot Reload Development Environment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# The development setup includes:
# - Hot reload for both frontend and backend
# - Development database (separate from production)
# - Debug mode enabled
# - Volume mounts for live code editing
```

### Development URLs
- **Frontend**: http://localhost:3000 (with hot reload)
- **Backend**: http://localhost:5001 (with hot reload)
- **Database**: localhost:5433

### Making Changes
```bash
# Backend changes
# Edit files in ./appointment-hub-backend/src/
# Changes will be reflected immediately

# Frontend changes  
# Edit files in ./appointment-hub-frontend/src/
# Changes will be reflected immediately

# Database changes
# Connect to development database
docker-compose -f docker-compose.dev.yml exec database psql -U dev_user -d appointment_hub_dev
```

## 🏭 Production Deployment

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose (see prerequisites)

# Create application directory
sudo mkdir -p /opt/appointment-hub
cd /opt/appointment-hub

# Copy your application files
# (upload via scp, git clone, etc.)
```

### 2. Production Configuration
```bash
# Create production environment file
cp .env.example .env

# Edit with production values
nano .env

# Set strong passwords and real API keys
# Configure SSL certificates
# Set up monitoring endpoints
```

### 3. SSL/HTTPS Setup
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy your SSL certificates
# nginx/ssl/certificate.crt
# nginx/ssl/private.key

# Update nginx configuration for HTTPS
# Edit nginx/nginx.conf
```

### 4. Deploy to Production
```bash
# Deploy with production profile
docker-compose --profile production up -d

# Or use the deployment script
./scripts/deploy.sh deploy
```

### 5. Production Monitoring
```bash
# Check service health
./scripts/deploy.sh health

# Monitor logs
./scripts/deploy.sh logs

# Check resource usage
docker stats
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Check all services
./scripts/deploy.sh health

# Manual health checks
curl http://localhost/health          # Frontend
curl http://localhost:5000/health     # Backend
docker-compose exec database pg_isready -U appointment_user -d appointment_hub
```

### Database Backup
```bash
# Create backup
./scripts/deploy.sh backup

# Restore from backup
./scripts/deploy.sh restore backup_20231225_120000.sql

# Manual backup
docker-compose exec database pg_dump -U appointment_user appointment_hub > backup.sql
```

### Log Management
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs database

# Follow logs in real-time
docker-compose logs -f

# Limit log output
docker-compose logs --tail=100 backend
```

### Resource Monitoring
```bash
# Check container resource usage
docker stats

# Check disk usage
docker system df

# Clean up unused resources
docker system prune -f
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :5000

# Stop conflicting services
sudo systemctl stop apache2  # If Apache is running
sudo systemctl stop nginx    # If Nginx is running

# Or change ports in docker-compose.yml
```

#### 2. Database Connection Issues
```bash
# Check database logs
docker-compose logs database

# Connect to database manually
docker-compose exec database psql -U appointment_user -d appointment_hub

# Reset database
docker-compose down
docker volume rm appointment-hub_postgres_data
docker-compose up -d
```

#### 3. Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend image
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Check Nginx configuration
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

#### 4. Backend API Errors
```bash
# Check backend logs
docker-compose logs backend

# Check environment variables
docker-compose exec backend env | grep -E "(DATABASE_URL|SECRET_KEY)"

# Restart backend service
docker-compose restart backend
```

### Debug Mode
```bash
# Enable debug mode for backend
docker-compose exec backend flask shell

# Check database tables
docker-compose exec database psql -U appointment_user -d appointment_hub -c "\dt"

# Check Redis connection
docker-compose exec redis redis-cli ping
```

## 🔒 Security Considerations

### 1. Environment Variables
- ✅ Change all default passwords
- ✅ Use strong, unique secret keys
- ✅ Never commit `.env` file to version control
- ✅ Use environment-specific configurations

### 2. Network Security
```bash
# Use custom networks (already configured)
# Limit exposed ports in production
# Configure firewall rules

# Example firewall setup (Ubuntu)
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw deny 5432   # Database (internal only)
sudo ufw enable
```

### 3. SSL/TLS Configuration
```bash
# Generate SSL certificates (Let's Encrypt example)
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Update nginx configuration for HTTPS
# Redirect HTTP to HTTPS
# Use strong SSL ciphers
```

### 4. Database Security
- ✅ Use strong database passwords
- ✅ Limit database access to application network
- ✅ Regular database backups
- ✅ Enable database logging for audit trails

### 5. Container Security
```bash
# Run containers as non-root users (already configured)
# Keep base images updated
# Scan images for vulnerabilities

# Update images regularly
docker-compose pull
docker-compose up -d
```

## 📈 Scaling & Performance

### Horizontal Scaling
```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Use load balancer (nginx service)
docker-compose --profile production up -d
```

### Performance Optimization
```bash
# Monitor resource usage
docker stats

# Optimize database
docker-compose exec database psql -U appointment_user -d appointment_hub -c "VACUUM ANALYZE;"

# Configure Redis for caching
# Update Redis configuration in docker-compose.yml
```

## 🚀 Advanced Configuration

### Custom Domain Setup
```bash
# Update environment variables
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com

# Configure reverse proxy
# Update nginx configuration
# Set up DNS records
```

### CI/CD Integration
```bash
# Example GitHub Actions workflow
# .github/workflows/deploy.yml

name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh user@server 'cd /opt/appointment-hub && git pull && ./scripts/deploy.sh deploy'
```

## 📞 Support

### Getting Help
- Check logs: `./scripts/deploy.sh logs`
- Check health: `./scripts/deploy.sh health`
- Review configuration: Verify `.env` file
- Check documentation: README.md and API docs

### Useful Commands Reference
```bash
# Deployment
./scripts/deploy.sh deploy     # Full deployment
./scripts/deploy.sh start      # Start services
./scripts/deploy.sh stop       # Stop services
./scripts/deploy.sh restart    # Restart services

# Monitoring
./scripts/deploy.sh status     # Service status
./scripts/deploy.sh health     # Health checks
./scripts/deploy.sh logs       # View logs

# Maintenance
./scripts/deploy.sh backup     # Database backup
./scripts/deploy.sh cleanup    # Clean up resources
```

---

## 🎉 Success!

Your AppointmentHub application should now be running successfully with Docker! 

**Access URLs:**
- **Frontend**: http://localhost (or your domain)
- **Backend API**: http://localhost:5000/api
- **Admin Panel**: Login with admin@demo.com / password123

**Next Steps:**
1. Configure your external API keys (Stripe, Calendly, etc.)
2. Set up SSL certificates for production
3. Configure monitoring and backups
4. Customize the application for your business needs

For additional support, refer to the main README.md and API documentation.

