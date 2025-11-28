#!/bin/bash

# AppointmentHub Deployment Script
# This script handles the complete deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="appointment-hub"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "Docker and Docker Compose are installed"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        log_warning ".env file not found. Creating from template..."
        cp .env.example .env
        log_warning "Please edit .env file with your actual configuration before continuing."
        log_warning "Press Enter to continue after editing .env file..."
        read
    fi
    log_success "Environment file found"
}

# Build images
build_images() {
    log_info "Building Docker images..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    log_success "Images built successfully"
}

# Start services
start_services() {
    log_info "Starting services..."
    docker-compose -f $COMPOSE_FILE up -d
    log_success "Services started successfully"
}

# Check service health
check_health() {
    log_info "Checking service health..."
    
    # Wait for services to be ready
    sleep 30
    
    # Check database
    if docker-compose -f $COMPOSE_FILE exec -T database pg_isready -U appointment_user -d appointment_hub; then
        log_success "Database is healthy"
    else
        log_error "Database health check failed"
        return 1
    fi
    
    # Check backend
    if curl -f http://localhost:5001/health > /dev/null 2>&1; then
        log_success "Backend is healthy"
    else
        log_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "Frontend is healthy"
    else
        log_error "Frontend health check failed"
        return 1
    fi
    
    log_success "All services are healthy"
}

# Show service status
show_status() {
    log_info "Service Status:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    log_info "Application URLs:"
    echo "  Frontend: http://localhost"
    echo "  Backend API: http://localhost:5001"
    echo "  Database: localhost:5432"
    echo ""
    log_info "Demo Accounts:"
    echo "  Admin: admin@demo.com / password123"
    echo "  Manager: manager@demo.com / password123"
    echo "  Client: client@demo.com / password123"
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    docker-compose -f $COMPOSE_FILE down
    log_success "Services stopped"
}

# Clean up (remove containers, networks, volumes)
cleanup() {
    log_warning "This will remove all containers, networks, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Cleaning up..."
        docker-compose -f $COMPOSE_FILE down -v --remove-orphans
        docker system prune -f
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# View logs
view_logs() {
    if [ -z "$1" ]; then
        docker-compose -f $COMPOSE_FILE logs -f
    else
        docker-compose -f $COMPOSE_FILE logs -f "$1"
    fi
}

# Backup database
backup_database() {
    log_info "Creating database backup..."
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    docker-compose -f $COMPOSE_FILE exec -T database pg_dump -U appointment_user appointment_hub > "$BACKUP_FILE"
    log_success "Database backup created: $BACKUP_FILE"
}

# Restore database
restore_database() {
    if [ -z "$1" ]; then
        log_error "Please provide backup file path"
        exit 1
    fi
    
    log_warning "This will replace the current database. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Restoring database from $1..."
        docker-compose -f $COMPOSE_FILE exec -T database psql -U appointment_user -d appointment_hub < "$1"
        log_success "Database restored successfully"
    else
        log_info "Database restore cancelled"
    fi
}

# Main script logic
case "$1" in
    "deploy")
        log_info "Starting deployment process..."
        check_docker
        check_env_file
        build_images
        start_services
        check_health
        show_status
        log_success "Deployment completed successfully!"
        ;;
    "start")
        start_services
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        start_services
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        view_logs "$2"
        ;;
    "backup")
        backup_database
        ;;
    "restore")
        restore_database "$2"
        ;;
    "cleanup")
        cleanup
        ;;
    "health")
        check_health
        ;;
    *)
        echo "AppointmentHub Deployment Script"
        echo ""
        echo "Usage: $0 {deploy|start|stop|restart|status|logs|backup|restore|cleanup|health}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full deployment (build, start, health check)"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Show service status and URLs"
        echo "  logs     - View logs (optionally specify service name)"
        echo "  backup   - Create database backup"
        echo "  restore  - Restore database from backup file"
        echo "  cleanup  - Remove all containers, networks, and volumes"
        echo "  health   - Check service health"
        echo ""
        echo "Examples:"
        echo "  $0 deploy"
        echo "  $0 logs backend"
        echo "  $0 restore backup_20231225_120000.sql"
        exit 1
        ;;
esac

