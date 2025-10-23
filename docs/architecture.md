# Architecture Overview

## Tech Stack

- Backend: Flask (Python)
- Database: SQLite with SQLAlchemy
- Authentication: Flask-Login
- Migrations: Flask-Migrate
- CSRF Protection: Flask-WTF
- Frontend: Jinja2 templates with HTML/CSS/JS (static files in /static)

## Key Files

- `main.py`: Entry point, runs the app
- `app.py`: App creation, config, DB init, seeding
- `routes.py`: All routes and views
- `models.py`: Database models (User, Category, Purchase, AuditLog)
- `config.py`: Configuration settings
- `templates/`: HTML templates
- `static/`: CSS, JS, uploads

## Database Schema

- Users: id, username, email, password, role
- Categories: id, name, description
- Purchases: id, user_id, description, amount, quantity, vendor, date_collected, purchase_type, category_id, attachment_url, notes, paid_on_collection
- AuditLogs: id, purchase_id, user_id, action, changes, timestamp

## Flow

- App initializes DB, seeds data
- Users login/register
- Shoppers upload purchases, which creates audit log
- Admins view aggregated data
