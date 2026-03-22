# AI-Based Resume Screening System

Practical BCA-level project built with Flask, SQLAlchemy, basic NLP, and a simple HTML/CSS/JS frontend.

## Features

- Recruiter registration and login
- Default admin login
- Job profile creation and management
- Single and bulk resume upload
- Resume parsing for skills, education, experience, contact details
- AI-based screening with scoring and ranking
- Result filtering and CSV export
- Admin health monitoring, logs, and issue tickets

## Tech Stack

- Backend: Flask, Flask-SQLAlchemy
- Database: SQLite by default, MySQL supported through `DATABASE_URL`
- NLP: spaCy, regex, scikit-learn TF-IDF
- File parsing: `pdfplumber`, `docx2txt`
- Frontend: HTML, CSS, JavaScript

## Project Structure

```text
backend/
  app.py
  config.py
  models/
  routes/
  services/
  utils/
frontend/
  *.html
  css/
  js/
database/
  schema.sql
```

## Setup

1. Create a virtual environment.
2. Copy `.env.example` to `.env` if you want custom database or admin credentials.
3. Install dependencies.
4. Start the Flask app.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in the browser.

## Default Admin Login

- Email: `admin@example.com`
- Password: `admin123`

## Recruiter Flow

1. Register from `/login.html`
2. Login as recruiter
3. Create a job profile
4. Upload resumes
5. Run AI screening
6. Open results and filter ranked candidates

## MySQL Option

Set `DATABASE_URL` in `.env` or environment variables.

Example:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost/resume_screening
```

## Notes

- SQLite is the default so the project runs locally without extra setup.
- `database/schema.sql` is included for MySQL-based submission/demo.
- If `pdfplumber` or `docx2txt` are missing, resume parsing for those files will fail until dependencies are installed.
