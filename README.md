# Expendiforge

Expendiforge is a full-stack web application built with Flask for tracking and managing purchases and expenses. It supports user roles including shoppers who can upload purchase details, admins who can view dashboards and analytics, and developers with special access.

## Features

- User authentication with registration, login, and role-based access
- Purchase uploading with attachments (PDF, JPG, PNG)
- Dashboard for admins with search, filters, totals, and charts data
- Export purchases to CSV
- Categories for organizing purchases
- Audit logging for changes
- Pre-seeded categories and dev users

## Requirements

- Python 3.x
- Dependencies managed via uv (see pyproject.toml and uv.lock)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Trading_Bot_Ecosystem.git
   cd Trading_Bot_Ecosystem
   ```

2. Install dependencies using uv:
   ```
   uv sync
   ```

3. Run the application:
   ```
   python main.py
   ```

The app will run on http://0.0.0.0:5000

## Usage

- Register as a new user or use pre-seeded accounts (e.g., username: admin, password: admin123)
- Shoppers: Go to /upload to add new purchases
- Admins: Access /dashboard to view and manage purchases
- Developers: Access /dev for dev home

## Database

Uses SQLite with database file `instance/expendiforge.db`. Migrations handled by Flask-Migrate.

## Configuration

See `config.py` for settings like upload folder, allowed extensions, etc.

## Contributing

[Add contributing guidelines here]

## License

[Specify license, e.g., MIT]
