# SALAH – Instant Legal Help Platform (Backend)

Salah is an instant legal help platform connecting users with Indian law students and junior lawyers.

## Tech Stack
- Django 6
- SQLite (development)
- Custom User Model
- Django Admin

## Core Backend Features
- Role-based users (Client / Lawyer)
- Lawyer profiles with service categories
- Consultation request system
- Wallet system
- Client-driven ratings

## Setup Instructions

```bash
git clone https://github.com/<your-username>/salah-backend.git
cd salah
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
