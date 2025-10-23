# Installation Guide

## Prerequisites

- Python 3.8 or higher
- uv package manager (install via `pip install uv` if needed)
- Git

## Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Trading_Bot_Ecosystem.git
   cd Trading_Bot_Ecosystem
   ```

2. Sync dependencies:
   ```
   uv sync
   ```

3. Initialize the database (automatically handled on first run)

4. Run the server:
   ```
   python main.py
   ```

5. Access the app at http://localhost:5000

## Environment Variables

- SESSION_SECRET: Set for production (default is a dev key)
