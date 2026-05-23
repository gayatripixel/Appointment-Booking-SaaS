# Product Requirements Document (PRD)
# AppointHub - Local Shop Booking Application

**Version:** 1.0
**Date:** December 5, 2025
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Product Overview
AppointHub is a web-based booking application built with Python Django that enables local shops (salons, barbershops, spas, fitness studios, medical clinics, etc.) to manage appointments and allow customers to book services online.

### 1.2 Problem Statement
Local service-based businesses often rely on phone calls, walk-ins, or manual scheduling, leading to:
- Missed appointments and no-shows
- Double bookings
- Inefficient staff utilization
- Lost revenue from after-hours booking requests
- Poor customer experience

### 1.3 Solution
A user-friendly web application that provides:
- Online booking for customers 24/7
- Calendar management for shop owners
- Staff and service management
- Automated reminders and notifications
- Business analytics and reporting

---

## 2. Goals and Objectives

### 2.1 Business Goals
- Enable local shops to accept online bookings
- Reduce no-show rates through automated reminders
- Increase booking efficiency and revenue
- Provide insights through analytics

### 2.2 Success Metrics
| Metric | Target |
|--------|--------|
| Booking completion rate | > 80% |
| No-show reduction | 50% decrease |
| Customer satisfaction | > 4.5/5 rating |
| Page load time | < 2 seconds |

---

## 3. User Personas

### 3.1 Shop Owner / Admin
- **Name:** Sarah, Salon Owner
- **Goals:** Manage staff schedules, track bookings, view business analytics
- **Pain Points:** Manual scheduling, double bookings, tracking no-shows

### 3.2 Staff Member
- **Name:** Mike, Barber
- **Goals:** View personal schedule, manage availability, track appointments
- **Pain Points:** Schedule conflicts, last-minute changes

### 3.3 Customer
- **Name:** Emma, Regular Customer
- **Goals:** Book appointments easily, receive reminders, manage bookings
- **Pain Points:** Phone booking during business hours only, forgetting appointments

---

## 4. Functional Requirements

### 4.1 User Management

#### 4.1.1 Authentication & Authorization
- [ ] User registration with email verification
- [ ] Login/logout functionality
- [ ] Password reset via email
- [ ] Role-based access control (Admin, Staff, Customer)

#### 4.1.2 User Profiles
- [ ] Customer profile (name, email, phone, booking history)
- [ ] Staff profile (name, bio, photo, services offered)
- [ ] Admin profile with full system access

### 4.2 Shop Management

#### 4.2.1 Shop Profile
- [ ] Shop registration and setup wizard
- [ ] Business information (name, address, phone, email)
- [ ] Business hours configuration
- [ ] Holiday/closure date management
- [ ] Shop logo and images upload

#### 4.2.2 Service Management
- [ ] Create/edit/delete services
- [ ] Service details (name, description, duration, price)
- [ ] Service categories
- [ ] Service-to-staff assignment
- [ ] Buffer time between appointments

#### 4.2.3 Staff Management
- [ ] Add/edit/remove staff members
- [ ] Staff working hours configuration
- [ ] Staff availability calendar
- [ ] Staff-to-service mapping
- [ ] Staff time-off management

### 4.3 Booking System

#### 4.3.1 Customer Booking Flow
- [ ] Browse available services
- [ ] Select service and preferred staff (optional)
- [ ] View available time slots
- [ ] Select date and time
- [ ] Provide contact information
- [ ] Booking confirmation
- [ ] Guest booking (without account)

#### 4.3.2 Booking Management
- [ ] View all bookings (calendar and list view)
- [ ] Filter bookings by date, staff, service, status
- [ ] Create manual bookings (walk-ins)
- [ ] Edit existing bookings
- [ ] Cancel bookings with reason
- [ ] Reschedule bookings
- [ ] Booking status tracking (Pending, Confirmed, Completed, Cancelled, No-show)

#### 4.3.3 Availability Management
- [ ] Real-time availability calculation
- [ ] Prevent double bookings
- [ ] Block time slots manually
- [ ] Recurring availability patterns
- [ ] Lead time and advance booking limits

### 4.4 Notifications

#### 4.4.1 Email Notifications
- [ ] Booking confirmation
- [ ] Booking reminder (24 hours before)
- [ ] Booking cancellation notice
- [ ] Booking modification notice
- [ ] Welcome email for new users

### 4.5 Dashboard & Analytics

#### 4.5.1 Admin Dashboard
- [ ] Today's appointments overview
- [ ] Upcoming bookings
- [ ] Recent activity feed
- [ ] Quick stats (total bookings, revenue, customers)

#### 4.5.2 Reports & Analytics
- [ ] Booking statistics (daily, weekly, monthly)
- [ ] Revenue reports
- [ ] Staff performance metrics
- [ ] Popular services analysis
- [ ] Customer retention metrics
- [ ] No-show tracking
- [ ] Export reports (CSV, PDF)

### 4.6 Customer Portal

#### 4.6.1 Customer Features
- [ ] View booking history
- [ ] Upcoming appointments
- [ ] Cancel/reschedule bookings
- [ ] Favorite shops/services

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Page load time: < 2 seconds
- API response time: < 500ms
- Support 100 concurrent users per shop
- 99.9% uptime target

### 5.2 Security
- HTTPS encryption
- Password hashing (Django's PBKDF2)
- CSRF protection
- SQL injection prevention
- XSS protection
- Rate limiting on authentication endpoints
- Session management
- GDPR compliance considerations

### 5.3 Scalability
- Horizontal scaling capability
- Database optimization
- Caching strategy (Redis)
- CDN for static assets

### 5.4 Usability
- Mobile-responsive design
- Intuitive navigation
- Accessibility (WCAG 2.1 AA)

### 5.5 Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Minimum screen width: 320px

---

## 6. Technical Architecture

### 6.1 Technology Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | Python Django 5.x |
| Database | PostgreSQL 15+ |
| Cache | Redis |
| Task Queue | Celery |
| Frontend | Django Templates + HTMX + Alpine.js |
| CSS Framework | Tailwind CSS |
| Email | Resend API |
| File Storage | Django Storage (Local/S3) |
| Deployment | Docker + Docker Compose |
| Web Server | Nginx + Gunicorn |

### 6.2 Database Schema (Core Models)

```
┌─────────────────┐     ┌─────────────────┐
│      User       │     │      Shop       │
├─────────────────┤     ├─────────────────┤
│ id              │     │ id              │
│ email           │     │ name            │
│ password        │     │ owner (FK User) │
│ first_name      │     │ address         │
│ last_name       │     │ phone           │
│ phone           │     │ email           │
│ role            │     │ description     │
│ created_at      │     │ logo            │
└─────────────────┘     │ is_active       │
                        └─────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Service     │     │     Staff       │     │  BusinessHours  │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id              │     │ id              │     │ id              │
│ shop (FK)       │     │ user (FK)       │     │ shop (FK)       │
│ name            │     │ shop (FK)       │     │ day_of_week     │
│ description     │     │ bio             │     │ open_time       │
│ duration        │     │ photo           │     │ close_time      │
│ price           │     │ is_active       │     │ is_closed       │
│ category        │     └─────────────────┘     └─────────────────┘
│ is_active       │              │
└─────────────────┘              │
        │                        │
        │    ┌───────────────────┘
        │    │
        ▼    ▼
┌─────────────────────┐
│   StaffService      │
├─────────────────────┤
│ staff (FK)          │
│ service (FK)        │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│      Booking        │
├─────────────────────┤
│ id                  │
│ shop (FK)           │
│ customer (FK User)  │
│ staff (FK)          │
│ service (FK)        │
│ date                │
│ start_time          │
│ end_time            │
│ status              │
│ notes               │
│ created_at          │
└─────────────────────┘
```

### 6.3 Application Structure

```
appointhub/
├── config/                 # Project configuration
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/          # User management
│   ├── shops/             # Shop management
│   ├── services/          # Service management
│   ├── staff/             # Staff management
│   ├── bookings/          # Booking system
│   ├── notifications/     # Email/SMS notifications
│   └── dashboard/         # Analytics & reporting
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS)
├── media/                 # User uploads
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
└── manage.py
```

---

## 7. User Interface Wireframes

### 7.1 Key Screens

1. **Landing Page** - Shop showcase, booking CTA
2. **Shop Registration** - Multi-step setup wizard
3. **Admin Dashboard** - Overview, stats, quick actions
4. **Service Management** - CRUD interface for services
5. **Staff Management** - Staff list, schedules
6. **Calendar View** - Daily/weekly/monthly booking calendar
7. **Booking Form** - Step-by-step booking wizard
8. **Customer Portal** - Booking history, profile

### 7.2 Design Principles
- Clean, modern interface
- Mobile-first approach
- Consistent color scheme and typography
- Clear call-to-action buttons
- Intuitive navigation

---

## 8. API Endpoints (REST)

### 8.1 Authentication
```
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/logout/
POST   /api/auth/password-reset/
```

### 8.2 Shops
```
GET    /api/shops/
POST   /api/shops/
GET    /api/shops/{id}/
PUT    /api/shops/{id}/
DELETE /api/shops/{id}/
```

### 8.3 Services
```
GET    /api/shops/{shop_id}/services/
POST   /api/shops/{shop_id}/services/
GET    /api/services/{id}/
PUT    /api/services/{id}/
DELETE /api/services/{id}/
```

### 8.4 Staff
```
GET    /api/shops/{shop_id}/staff/
POST   /api/shops/{shop_id}/staff/
GET    /api/staff/{id}/
PUT    /api/staff/{id}/
GET    /api/staff/{id}/availability/
```

### 8.5 Bookings
```
GET    /api/bookings/
POST   /api/bookings/
GET    /api/bookings/{id}/
PUT    /api/bookings/{id}/
DELETE /api/bookings/{id}/
GET    /api/availability/?shop={id}&date={date}&service={id}
```

---

## 9. Development Scope

### Core Features
**Scope:**
- User authentication (registration, login, roles)
- Shop setup and management
- Service CRUD operations
- Staff management
- Basic booking system
- Email notifications
- Admin dashboard
- Customer booking portal

**Deliverables:**
- Functional booking system
- Admin panel for shop management
- Customer-facing booking interface
- Email confirmations and reminders

---

## 10. Testing Strategy

### 10.1 Testing Types
- **Unit Tests:** Django TestCase for models, views, utils
- **Integration Tests:** API endpoint testing
- **E2E Tests:** Selenium/Playwright for critical flows
- **Performance Tests:** Load testing with Locust

### 10.2 Test Coverage Target
- Minimum 80% code coverage
- 100% coverage for booking logic

### 10.3 CI/CD Pipeline
- Automated tests on PR
- Code quality checks (flake8, black)
- Security scanning
- Automated deployment to staging

---

## 11. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Double booking bug | High | Medium | Comprehensive testing, database locks |
| Email delivery issues | Medium | Medium | Use Resend API with good deliverability |
| Security breach | High | Low | Security audit, follow OWASP guidelines |
| Performance issues | Medium | Medium | Caching, query optimization, load testing |
| Scope creep | Medium | High | Strict scope adherence, MVP focus |

---

## 12. Success Criteria

### 12.1 Launch Criteria
- [ ] All core features implemented
- [ ] 80%+ test coverage
- [ ] Security audit passed
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] User acceptance testing passed

### 12.2 Post-Launch Metrics
- User registration rate
- Booking completion rate
- System uptime
- Customer satisfaction scores
- Bug resolution time

---

## 13. Appendix

### 13.1 Glossary
- **Booking:** An appointment reservation
- **Service:** A specific offering (e.g., haircut, massage)
- **Staff:** Employee who provides services
- **Shop:** The business entity
- **Slot:** Available time period for booking

### 13.2 References
- Django Documentation: https://docs.djangoproject.com/
- HTMX Documentation: https://htmx.org/docs/
- Tailwind CSS: https://tailwindcss.com/docs
- Resend API: https://resend.com/docs

### 13.3 Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-05 | Claude | Initial draft |
| 1.1 | 2025-12-05 | Claude | Switched to Resend API, removed Phase 2/3, focused on MVP |

---

**Document Status:** Ready for Review
**Next Steps:** Stakeholder review and approval before development begins
