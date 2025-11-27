# AppointmentHub - Complete Appointment Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/react-19.1.0-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

A production-ready, full-stack appointment management system designed for businesses of all sizes. Built with modern technologies and enterprise-level architecture, AppointmentHub provides comprehensive booking, payment, and customer management capabilities.

## 🐳 Quick Start with Docker (Recommended)

### Prerequisites
- Docker & Docker Compose
- Git

### One-Command Deployment
```bash
git clone https://github.com/ale161/appointment-hub-full-docker.git
cd appointment-hub-full-docker
cp .env.example .env
# Edit .env with your settings
./scripts/deploy.sh deploy
```

**Access URLs:**
- Frontend: http://localhost
- Backend API: http://localhost:5000
- Database: localhost:5432 (internal)

**Demo Accounts:**
- Admin: `admin@demo.com` / `password123`
- Manager: `manager@demo.com` / `password123`
- Client: `client@demo.com` / `password123`

### Docker Services
- **PostgreSQL**: Primary database with persistent storage
- **Redis**: Caching and session management
- **Flask Backend**: Gunicorn WSGI server (4 workers)
- **React Frontend**: Nginx-served with gzip compression
- **Nginx Load Balancer**: SSL termination and load balancing (optional)

## 🌟 Features

### Core Functionality
- **Multi-tenant Architecture**: Support for multiple businesses with complete data isolation
- **Role-based Access Control**: Admin, Store Manager, and Client roles with appropriate permissions
- **Advanced Booking System**: Flexible scheduling with calendar integration and automated reminders
- **Secure Payment Processing**: Integrated Stripe payments with support for deposits and full payments
- **Real-time Notifications**: SMS and email notifications via EasySMS integration
- **Calendar Synchronization**: Seamless integration with Calendly API v2

### Business Features
- **Store Management**: Complete business profile management with photos and descriptions
- **Service Catalog**: Flexible service offerings with pricing and duration settings
- **Analytics Dashboard**: Comprehensive insights into bookings, revenue, and customer behavior
- **Subscription Management**: Tiered pricing plans with automated billing
- **Customer Management**: Complete customer profiles and booking history

### Technical Features
- **Modern UI/UX**: Responsive design built with React, Tailwind CSS, and shadcn/ui
- **RESTful API**: Well-documented Flask API with JWT authentication
- **Database Flexibility**: PostgreSQL for production, SQLite for development
- **External Integrations**: Ready-to-use integrations with popular services
- **Production Ready**: Comprehensive error handling, logging, and security measures

## 🏗️ Architecture

### Backend (Flask API)
```
appointment-hub-backend/
├── src/
│   ├── main.py              # Application entry point
│   ├── models/              # Database models
│   │   ├── user.py          # User management
│   │   ├── store.py         # Store/business management
│   │   ├── service.py       # Service offerings
│   │   ├── booking.py       # Appointment bookings
│   │   ├── payment.py       # Payment processing
│   │   └── subscription.py  # Subscription management
│   ├── routes/              # API endpoints
│   │   ├── auth.py          # Authentication
│   │   ├── booking.py       # Booking management
│   │   ├── payment.py       # Payment processing
│   │   └── store.py         # Store management
│   └── utils/               # Utility functions
│       ├── auth.py          # Authentication helpers
│       ├── calendly_integration.py
│       ├── easysms_integration.py
│       └── stripe_integration.py
├── requirements.txt         # Python dependencies
└── create_demo_data.py     # Demo data creation
```

### Frontend (React Application)
```
appointment-hub-frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/              # shadcn/ui components
│   │   ├── Layout.jsx       # Dashboard layout
│   │   ├── PublicLayout.jsx # Public pages layout
│   │   └── ProtectedRoute.jsx
│   ├── contexts/            # React contexts
│   │   └── AuthContext.jsx  # Authentication state
│   ├── pages/               # Page components
│   │   ├── HomePage.jsx     # Landing page
│   │   ├── LoginPage.jsx    # Authentication
│   │   ├── DashboardPage.jsx # Main dashboard
│   │   └── BookingsPage.jsx # Booking management
│   └── App.jsx              # Main application
├── package.json             # Node.js dependencies
└── tailwind.config.js       # Tailwind CSS configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL (for production) or SQLite (for development)

### Backend Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd appointment-hub/appointment-hub-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   export FLASK_ENV=development
   export JWT_SECRET_KEY=your-secret-key
   export STRIPE_SECRET_KEY=your-stripe-key
   export CALENDLY_API_KEY=your-calendly-key
   export EASYSMS_API_KEY=your-easysms-key
   ```

5. **Initialize database**
   ```bash
   python -c "from src.main import app, db; app.app_context().push(); db.create_all()"
   ```

6. **Create demo data (optional)**
   ```bash
   python create_demo_data.py
   ```

7. **Start the server**
   ```bash
   python src/main.py
   ```

   The API will be available at `http://localhost:5002`

### Frontend Setup
1. **Navigate to frontend directory**
   ```bash
   cd ../appointment-hub-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173`

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/appointment_hub

# External API Keys
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
CALENDLY_API_KEY=your-calendly-api-key
EASYSMS_API_KEY=your-easysms-api-key
EASYSMS_API_SECRET=your-easysms-secret

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

#### Frontend (.env.local)
```env
VITE_API_BASE_URL=http://localhost:5002/api
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## 📊 Database Schema

The application uses a comprehensive database schema designed for scalability and multi-tenancy:

### Core Tables
- **users**: User accounts with role-based access
- **stores**: Business/store information
- **services**: Service offerings per store
- **bookings**: Appointment bookings
- **payments**: Payment transactions
- **subscriptions**: Subscription management
- **notifications**: Email/SMS notification tracking

### Key Relationships
- Users can be clients, store managers, or administrators
- Store managers are associated with specific stores
- Bookings link clients, services, and stores
- Payments track financial transactions per booking
- Subscriptions manage billing for store owners

## 🔐 Authentication & Authorization

### JWT-based Authentication
- Secure token-based authentication
- Automatic token refresh
- Role-based access control

### User Roles
1. **Client**: Can browse stores, book appointments, manage their bookings
2. **Store Manager**: Can manage their store, services, bookings, and view analytics
3. **Admin**: Full system access, can manage all stores and users

### Security Features
- Password hashing with Werkzeug
- CORS protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## 💳 Payment Integration

### Stripe Integration
- Secure payment processing
- Support for one-time payments and subscriptions
- Webhook handling for payment confirmations
- Refund processing
- Payment method management

### Supported Payment Methods
- Credit/Debit cards
- Digital wallets (Apple Pay, Google Pay)
- Bank transfers (where supported)

## 📱 External Integrations

### Calendly API v2
- Calendar synchronization
- Automatic booking creation
- Real-time availability updates
- Webhook notifications

### EasySMS Integration
- SMS notifications for booking confirmations
- Appointment reminders
- Cancellation notifications
- Custom message templates

## 🎨 UI/UX Design

### Design System
- **Framework**: React with TypeScript support
- **Styling**: Tailwind CSS for utility-first styling
- **Components**: shadcn/ui for consistent, accessible components
- **Icons**: Lucide React for modern iconography
- **Animations**: Framer Motion for smooth interactions

### Responsive Design
- Mobile-first approach
- Tablet and desktop optimizations
- Touch-friendly interactions
- Accessibility compliance (WCAG 2.1)

### Key Pages
1. **Landing Page**: Marketing-focused with features and pricing
2. **Authentication**: Clean login/register forms
3. **Dashboard**: Role-specific dashboards with analytics
4. **Booking Management**: Comprehensive booking interface
5. **Store Management**: Business profile and service management

## 🚀 Deployment

### Docker Deployment (Recommended)

#### Option 1: Production Docker Deployment
```bash
# Full production stack with PostgreSQL and Redis
docker-compose up -d

# Check status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs

# Health check
./scripts/deploy.sh health
```

**Services included:**
- PostgreSQL database with persistent storage
- Redis for caching and sessions
- Flask backend with Gunicorn (4 workers)
- React frontend served by Nginx
- Automatic SSL/HTTPS support (with certificates)

#### Option 2: Development Docker Environment
```bash
# Development with hot reload
docker-compose -f docker-compose.dev.yml up -d

# Frontend: http://localhost:3000 (hot reload)
# Backend: http://localhost:5001 (hot reload)
```

**Development features:**
- Hot reload for both frontend and backend
- Separate development database
- Debug mode enabled
- Volume mounts for live code editing

#### Option 3: Automated Deployment Script
```bash
# Complete deployment with health checks
./scripts/deploy.sh deploy

# Available commands:
./scripts/deploy.sh start      # Start services
./scripts/deploy.sh stop       # Stop services
./scripts/deploy.sh restart    # Restart services
./scripts/deploy.sh status     # Show service status
./scripts/deploy.sh health     # Run health checks
./scripts/deploy.sh logs       # View logs (all services)
./scripts/deploy.sh logs backend  # View specific service logs
./scripts/deploy.sh backup     # Create database backup
./scripts/deploy.sh restore backup.sql  # Restore database
./scripts/deploy.sh cleanup    # Remove all containers and volumes
```

#### Docker Configuration Files

**docker-compose.yml** (Production)
- PostgreSQL with persistent volumes
- Redis for caching
- Flask backend with Gunicorn
- React frontend with Nginx
- Network isolation and security

**docker-compose.dev.yml** (Development)
- Hot reload enabled
- Development database
- Debug logging
- Volume mounts for code changes

#### Environment Configuration
```bash
# Copy and edit environment variables
cp .env.example .env

# Key variables to configure:
DB_PASSWORD=secure_password_123
SECRET_KEY=your-32-character-secret-key
JWT_SECRET_KEY=your-32-character-jwt-key
STRIPE_SECRET_KEY=sk_test_your_stripe_key
CALENDLY_ACCESS_TOKEN=your_calendly_token
EASYSMS_API_KEY=your_easysms_key
```

#### SSL/HTTPS Setup (Production)
```bash
# Create SSL directory and add certificates
mkdir -p nginx/ssl
# Copy your certificate.crt and private.key to nginx/ssl/

# Deploy with SSL support
docker-compose --profile production up -d
```

#### Scaling and Load Balancing
```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Enable Nginx load balancer
docker-compose --profile production up -d
```

#### Monitoring and Maintenance
```bash
# Monitor resource usage
docker stats

# View container logs
docker-compose logs -f

# Database backup
./scripts/deploy.sh backup

# Clean up unused resources
docker system prune -f
```

### Production Deployment Options

#### Option 1: Traditional Server Deployment
1. **Server Requirements**
   - Ubuntu 20.04+ or CentOS 8+
   - Python 3.11+
   - PostgreSQL 13+
   - Nginx (reverse proxy)
   - SSL certificate

2. **Backend Deployment**
   ```bash
   # Install system dependencies
   sudo apt update
   sudo apt install python3.11 python3.11-venv postgresql nginx

   # Clone and setup application
   git clone <repository-url>
   cd appointment-hub/appointment-hub-backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Configure PostgreSQL
   sudo -u postgres createdb appointment_hub
   sudo -u postgres createuser appointment_user

   # Setup environment variables
   cp .env.example .env
   # Edit .env with production values

   # Run with Gunicorn
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5002 src.main:app
   ```

3. **Frontend Deployment**
   ```bash
   cd ../appointment-hub-frontend
   npm install
   npm run build
   
   # Serve with Nginx
   sudo cp -r dist/* /var/www/html/
   ```

#### Option 2: Docker Deployment
1. **Backend Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY src/ ./src/
   EXPOSE 5002
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "src.main:app"]
   ```

2. **Frontend Dockerfile**
   ```dockerfile
   FROM node:18-alpine AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm install
   COPY . .
   RUN npm run build

   FROM nginx:alpine
   COPY --from=builder /app/dist /usr/share/nginx/html
   EXPOSE 80
   ```

3. **Docker Compose**
   ```yaml
   version: '3.8'
   services:
     backend:
       build: ./appointment-hub-backend
       ports:
         - "5002:5002"
       environment:
         - DATABASE_URL=postgresql://user:pass@db:5432/appointment_hub
       depends_on:
         - db

     frontend:
       build: ./appointment-hub-frontend
       ports:
         - "80:80"
       depends_on:
         - backend

     db:
       image: postgres:13
       environment:
         POSTGRES_DB: appointment_hub
         POSTGRES_USER: user
         POSTGRES_PASSWORD: password
       volumes:
         - postgres_data:/var/lib/postgresql/data

   volumes:
     postgres_data:
   ```

#### Option 3: Cloud Platform Deployment

**Heroku Deployment**
```bash
# Backend
cd appointment-hub-backend
heroku create appointment-hub-api
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main

# Frontend
cd ../appointment-hub-frontend
heroku create appointment-hub-app
heroku buildpacks:set https://github.com/mars/create-react-app-buildpack
git push heroku main
```

**AWS Deployment**
- Use AWS Elastic Beanstalk for the backend
- Deploy frontend to S3 with CloudFront
- Use RDS for PostgreSQL database
- Configure Route 53 for custom domain

## 📈 Monitoring & Analytics

### Built-in Analytics
- Booking conversion rates
- Revenue tracking
- Customer retention metrics
- Popular services analysis
- Peak booking times

### Monitoring Tools
- Application performance monitoring
- Error tracking and logging
- Database performance metrics
- API response time monitoring

## 🧪 Testing

### Backend Testing
```bash
cd appointment-hub-backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd appointment-hub-frontend
npm run test
```

### End-to-End Testing
```bash
npm run test:e2e
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/React code
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure mobile responsiveness for UI changes

## 📝 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh JWT token

### Booking Endpoints
- `GET /api/bookings` - List user bookings
- `POST /api/bookings` - Create new booking
- `GET /api/bookings/{id}` - Get booking details
- `PUT /api/bookings/{id}` - Update booking
- `DELETE /api/bookings/{id}` - Cancel booking

### Store Management Endpoints
- `GET /api/stores` - List stores
- `POST /api/stores` - Create store (store managers only)
- `GET /api/stores/{id}` - Get store details
- `PUT /api/stores/{id}` - Update store
- `GET /api/stores/{id}/services` - List store services

### Payment Endpoints
- `POST /api/payments/intent` - Create payment intent
- `POST /api/payments/confirm` - Confirm payment
- `GET /api/payments/{id}` - Get payment details
- `POST /api/payments/{id}/refund` - Process refund

## 🔧 Troubleshooting

### Common Issues

**Database Connection Issues**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Reset database
python -c "from src.main import app, db; app.app_context().push(); db.drop_all(); db.create_all()"
```

**Frontend Build Issues**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

**API CORS Issues**
- Ensure CORS is properly configured in Flask app
- Check that frontend URL is in allowed origins
- Verify API base URL in frontend configuration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [React](https://reactjs.org/) - Frontend library
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [shadcn/ui](https://ui.shadcn.com/) - UI components
- [Stripe](https://stripe.com/) - Payment processing
- [Calendly](https://calendly.com/) - Calendar integration

## 📞 Support

For support, email support@appointmenthub.com or join our Slack channel.

---

**Built with ❤️ by the AppointmentHub Team**

