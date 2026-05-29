# 📅 AppointHub

<div align="center">

**A high-performance, production-ready appointment booking platform built with Modern Django**

[![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-green?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)
[![HTMX](https://img.shields.io/badge/HTMX-2.x-3366CC?style=flat-square&logo=htmx&logoColor=white)](https://htmx.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.x-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[📸 Screenshots](https://github.com/gayatripixel/Appointment-Booking-SaaS#-screenshots)
</div>

---

## 🎯 Overview

AppointHub is a comprehensive appointment scheduling and business management solution designed for service-based businesses like salons, spas, clinics, and consulting firms. Built with **Modern Django architecture**, it leverages **HTMX** for dynamic interactivity and **Alpine.js** for lightweight frontend logic—delivering **SPA-like speed without the complexity** of a JavaScript framework.

### Why AppointHub?

- **Production-Ready** - Built with industry best practices, clean architecture, and scalable infrastructure
- **Modern Django Stack** - Django 5.2 + HTMX + Alpine.js for seamless, reactive user experiences
- **SPA-like Performance** - Dynamic page updates without full reloads, zero JavaScript framework overhead
- **Responsive Design** - Beautiful UI that works seamlessly on all devices
- **Secure** - Token-based authentication, password hashing, and CSRF protection
- **Analytics Dashboard** - Visual insights into business performance

---

## ✨ Features

### 🏠 Landing Page
- Modern, responsive hero section with gradient backgrounds
- Interactive dashboard preview with animated charts
- Feature showcase with hover effects
- Pricing plans (Free, Pro, Enterprise)
- "How It Works" step-by-step guide
- Professional footer with social links

### 📊 Dashboard & Analytics
- Real-time business metrics and KPIs
- Revenue tracking with interactive line charts
- Weekly appointment activity visualization (bar chart)
- Popular services distribution (doughnut chart)
- Today's schedule at a glance
- Recent activity feed with live updates
- Month-to-month navigation

### 📅 Appointment Management
- Full CRUD operations for appointments
- Status tracking (Pending, Confirmed, Completed, Cancelled, No-Show)
- Advanced filtering by date, status, staff, and service
- Real-time search functionality
- Date and time slot management
- Customer and staff assignment
- Appointment notes and history

### 💼 Service Management
- Service catalog with categories
- Pricing and duration configuration
- Active/Inactive status toggle
- Booking statistics per service
- Service color coding
- Category organization

### 👥 Staff Management
- Staff profiles with contact information
- Availability status (Available, Busy, Off)
- Service assignments and specializations
- Performance ratings and reviews
- Weekly appointment tracking
- Working hours configuration

### 👤 Customer Management
- Customer database with detailed profiles
- VIP/Regular/New customer segmentation
- Visit history and spending tracking
- Contact information management
- Customer notes and preferences
- Total visits and lifetime value tracking

### ⚙️ Settings & Preferences
- Notification preferences (Email, SMS, Reminders)
- Privacy controls
- Password management with secure reset
- Profile customization
- Account management

### 🔐 Authentication & Security
- Secure user registration and login
- Email verification system
- Password reset with token-based links
- Session management
- CSRF protection
- Clean, modern auth UI

---

## 📸 Screenshots

<div align="center">

### 🏠 Homepage

![Homepage Hero](docs/screenshots/Homepage-1.png)
*Modern SaaS landing page for appointment booking with responsive hero section, CTA buttons, and service highlights.*

![Homepage Services](docs/screenshots/Homepage-2.png)
*Showcases salon booking, clinic appointments, spa & wellness services, and simple 3-step booking workflow.*

![Homepage Features](docs/screenshots/Homepage-3.png)
*Displays powerful platform features including real-time availability, smart scheduling, secure booking, and multi-service support.*

![Homepage Pricing](docs/screenshots/Homepage-4.png)
*Flexible subscription plans with booking features, priority support, unlimited appointments, and premium experience options.*

### 📊 Dashboard

![Dashboard](docs/screenshots/Dashboard-1.png)
*Business management dashboard displaying appointments, bookings, customers, monthly revenue, and quick action shortcuts.*

![Dashboard Analytics](docs/screenshots/Dashboard-2.png)
*Interactive analytics section with revenue trends, popular services, recent customer activity, and booking insights.*


### 💼 Services
![Services](docs/screenshots/Service-page.png)
*Service catalog with categories, pricing, and duration*

### 👥 Staff Management
![Staff](docs/screenshots/Staff-page.png)
*Team overview with availability status and performance metrics*

### 👤 Customers
![Customers](docs/screenshots/Customer-page.png)
*Customer database with segmentation and visit history*

### ⚙️ Settings
![Settings](docs/screenshots/User-setting.png)
*User preferences, notifications, and account management*

### 🔐 Authentication
![Login](docs/screenshots/Login-page.png)
*Secure authentication with modern, clean UI*

</div>

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.13** | Core programming language |
| **Django 5.2** | High-performance web framework with batteries included |
| **PostgreSQL** | Production-grade relational database (SQLite for development) |
| **Celery** | Asynchronous task queue for background jobs (email notifications, scheduled tasks) |
| **Redis** | High-performance caching layer and message broker for Celery task distribution |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTMX** | Dynamic HTML updates with SPA-like interactivity—no JavaScript framework required |
| **Alpine.js** | Lightweight reactivity for UI state management and DOM manipulation |
| **Tailwind CSS** | Utility-first CSS framework for rapid, consistent styling |
| **Chart.js** | Interactive data visualization for analytics dashboards |

### Infrastructure & DevOps
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization for consistent development and production environments |
| **Git** | Version control and collaborative development |
| **Resend** | Reliable transactional email delivery service |

---

## 🚀 Installation

### Prerequisites
- Python 3.11+
- pip or pipenv
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/gayatripixel/Appointment-Booking-SaaS
cd AppointHub

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/development.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see the application.

---

## 📁 Project Structure

```
AppointHub/
├── apps/
│   ├── accounts/       # User authentication & profiles
│   ├── bookings/       # Appointment booking logic
│   ├── dashboard/      # Main dashboard views
│   ├── notifications/  # Email & notification services
│   ├── services/       # Service management
│   ├── shops/          # Business/shop configuration
│   └── staff/          # Staff management
├── config/
│   ├── settings/       # Environment-specific settings
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── celery.py
├── templates/          # Django templates
│   ├── accounts/
│   ├── dashboard/
│   ├── emails/
│   └── base.html
├── static/             # Static assets
├── media/              # User uploads
├── requirements/       # Dependency files
└── docker/             # Docker configuration
```

---

## 🎨 Design System

### Color Palette
| Color | Hex | Usage |
|-------|-----|-------|
| Indigo | `#667eea` | Primary brand color |
| Purple | `#764ba2` | Secondary brand color |
| White | `#ffffff` | Backgrounds |
| Gray 50 | `#f9fafb` | Page backgrounds |
| Gray 800 | `#1f2937` | Text |

### UI Components
- **Clean White Design** - Modern, minimalist white backgrounds
- **Gradient Buttons** - Indigo to purple gradient CTAs
- **Animated Charts** - Growing bars and smooth transitions
- **Hover Effects** - Subtle scale and shadow on cards
- **Responsive Grid** - Mobile-first layout system
- **Inter Font** - Clean, modern typography

---

## 🔧 Configuration

### Environment Variables

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Production)
DATABASE_URL=postgres://user:pass@host:5432/dbname

# Email (Resend)
RESEND_API_KEY=your-resend-api-key

# Redis
REDIS_URL=redis://localhost:6379/0
```

---

## 📈 Roadmap

- [x] Dashboard with analytics
- [x] Appointment management
- [x] Service catalog
- [x] Staff management
- [x] Customer database
- [x] User settings

---

## 🧪 Testing & Quality Assurance

AppointHub uses Django's built-in testing framework to ensure system reliability and maintain code quality across all modules.

```bash
# Run the full test suite
python manage.py test

# Run tests for a specific app
python manage.py test apps.bookings

# Run tests with verbosity
python manage.py test --verbosity=2
```

The project follows standard Django testing conventions with unit tests for models, views, and forms to ensure consistent behavior across releases.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---


<div align="center">

⭐ Star this repo if you find it helpful!

Built with **Django 5.2** • **HTML** • **Alpine.js** • **Tailwind CSS**

</div>
