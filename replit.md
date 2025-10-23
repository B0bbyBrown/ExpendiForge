# ExpendiForge

**Tagline:** "Forge Financial Clarity from Every Purchase."

## Overview
ExpendiForge is a company shopping tracker MVP built with Flask. It allows shoppers to upload purchase details and admins to view comprehensive analytics dashboards. The application focuses on tracking expenditures for products and services paid on collection, without requiring full ERP integration.

## Current State
Fully functional Flask application with:
- User authentication (registration, login, logout)
- Three-role access control (shopper, admin, dev)
- Purchase upload with file attachments
- Admin dashboard with filtering, search, and visualizations
- CSV export functionality
- Audit logging for all purchase actions
- Responsive Bootstrap UI
- Developer testing environment with access to both UIs

## Recent Changes
**October 23, 2025 (Latest):** Added three-role system
- Implemented dev role with access to both shopper and admin interfaces
- Created dev home page with links to upload and dashboard
- Updated navigation to show role-specific menu items
- Secured dev role to prevent public registration (only via seed data)

**October 23, 2025:** Initial project setup
- Created complete Flask application structure
- Implemented SQLAlchemy models (Users, Categories, Purchases, Audit Logs)
- Set up Flask-Login authentication with CSRF protection
- Built responsive UI with Bootstrap 5
- Added Chart.js visualizations (pie chart for categories, bar chart for monthly trends)
- Configured CSV export with filtering
- Set up automated category seeding
- Created workflow to run Flask development server
- Fixed date_collected default to use callable for fresh timestamps

## Project Architecture

### Tech Stack
- **Backend:** Flask 3.1.2, SQLAlchemy 2.0, Flask-Login, Flask-Migrate
- **Database:** SQLite (file-based, ready for PostgreSQL migration)
- **Frontend:** HTML/Jinja2 templates, Bootstrap 5, Chart.js 4.4
- **Security:** Werkzeug password hashing, CSRF protection, input sanitization
- **File Storage:** Local filesystem (static/uploads)

### Database Schema
1. **Users:** id, username, email, password (hashed), role, created_at
2. **Categories:** id, name, description
3. **Purchases:** id, user_id, description, amount, quantity, vendor, date_collected, purchase_type, category_id, attachment_url, notes, paid_on_collection, created_at
4. **Audit Logs:** id, purchase_id, user_id, action, changes (JSON), timestamp

### File Structure
```
.
├── app.py                  # Flask app initialization & setup
├── config.py              # Configuration (DB URI, upload settings, secrets)
├── models.py              # SQLAlchemy models
├── routes.py              # All application routes
├── main.py                # Application entrypoint
├── templates/             # Jinja2 templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── upload.html
│   └── dashboard.html
└── static/
    ├── css/
    ├── js/
    └── uploads/           # User-uploaded files (PDF, JPG, PNG)
```

### User Roles
1. **Shopper** - Can upload purchases, access /upload only
2. **Admin** - Can view analytics dashboard, access /dashboard and /export only
3. **Dev** - Can access both shopper and admin interfaces (for testing)

### Dev Credentials (Pre-seeded)
- **Shopper:** username: `shopper`, password: `shopper123`
- **Admin:** username: `admin`, password: `admin123`
- **Dev:** username: `dev`, password: `dev123`

**Security Note:** Dev role cannot be created through public registration - only through seed_dev_users() in app.py.

### Routes
- `/` - Home (redirects based on auth/role)
- `/register` - User registration (GET/POST) - allows shopper/admin only
- `/login` - User login (GET/POST)
- `/logout` - Logout
- `/dev` - Developer home page (dev only)
- `/upload` - Purchase upload form (shoppers and dev)
- `/dashboard` - Analytics dashboard (admins and dev)
- `/export` - CSV export with filters (admins and dev)

### Key Features
1. **Authentication:** Flask-Login with role-based access (shopper/admin)
2. **Purchase Upload:** Supports file attachments (PDF/JPG/PNG, max 5MB)
3. **Dashboard Analytics:**
   - Total spend, purchase count, type breakdowns
   - Pie chart: spending by category
   - Bar chart: monthly spending trends
   - High-spend alerts (>$1000) with visual indicators
4. **Filtering:** Search, category, vendor, type, date range
5. **CSV Export:** Download filtered purchase data
6. **Audit Logging:** All purchase actions tracked with JSON change logs
7. **Data Validation:** Server-side checks for required fields, positive values, file types

### Security Features
- Passwords hashed with Werkzeug (pbkdf2:sha256)
- Secure file uploads with filename sanitization
- Role-based route protection
- Input validation and sanitization
- Session management with Flask-Login
- Check constraints on database (amount > 0, quantity > 0)

### Default Categories
- Office Supplies
- Electronics
- Services
- Miscellaneous

## User Preferences
None specified yet.

## Future Enhancements (Post-MVP)
- Migrate to PostgreSQL for production scalability
- Add purchase editing and deletion with audit trail
- Implement OCR for automatic receipt data extraction
- Add email notifications for high-value purchases
- Create PWA wrapper for mobile access
- Advanced analytics with custom date comparisons
- Budget tracking and spending limits
- Multi-currency support
