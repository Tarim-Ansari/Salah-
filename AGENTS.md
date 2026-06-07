# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Critical Non-Obvious Patterns

### Wallet System Architecture
- Wallet operations use custom [`credit()`](accounts/models.py:110) and [`debit()`](accounts/models.py:117) methods on the Wallet model, NOT direct balance manipulation
- [`debit()`](accounts/models.py:117) returns `False` on insufficient funds - MUST check return value before proceeding
- Transaction records are auto-created by wallet methods - do NOT create manually
- Despite README claiming `transaction.atomic`, the codebase does NOT use Django's atomic transactions for wallet operations

### Video Consultation Billing
- Billing starts AFTER 2-minute grace period (hardcoded in client_logic.js)
- Session state persists in localStorage with key pattern `salah_session_{SESSION_ID}` - enables page refresh without losing timer
- Payment processing happens in [`left-meeting`](accounts/static/accounts/js/video/client_logic.js:250) event, NOT on button click
- Room creation via Daily.co API silently fails if room exists (intentional, see [`join_room`](accounts/views.py:379))

### Y-Splitter Audio Recording (Critical Implementation Detail)
- Audio recording uses `navigator.mediaDevices.getUserMedia()` directly, NOT Daily.co's `participants.local.tracks.audio.track` (which returns undefined)
- MediaRecorder MUST be started with timeslice parameter: `audioRecorder.start(1000)` - without it, `ondataavailable` never fires and no chunks are collected
- Mute sync polls Daily.co state every 500ms using `call.localAudio()` and pauses/resumes MediaRecorder accordingly
- Audio upload happens in `left-meeting` event with 2-second wait for async upload completion

### Authentication & Routing
- Username field stores email (see [`signup_view`](accounts/views.py:54): `username=email`)
- Role-based template routing in [`join_room`](accounts/views.py:398) checks exact user match against consultation.lawyer/client
- Custom user model at [`AUTH_USER_MODEL = 'accounts.User'`](core/settings.py:113)

### Rating System Gotcha
- LawyerProfile.rating field must be manually updated when Rating objects are created
- [`rate_lawyer_api`](accounts/views.py:485) calculates average and saves to profile - this pattern is NOT automatic

### Environment Configuration
- Daily.co credentials required: `DAILY_API_KEY`, `DAILY_SUBDOMAIN`
- Groq API key required for audio transcription: `GROQ_API_KEY`
- CSRF_TRUSTED_ORIGINS includes ngrok patterns for local HTTPS testing (WebRTC requirement)
- DEBUG mode controlled by string comparison: `os.getenv("DEBUG") == "True"` (not boolean)

### Database Migrations
- Run `python manage.py makemigrations` before `migrate` (not automatic)
- SQLite used for development (see [`DATABASES`](core/settings.py:65))

## Commands
```bash
# Setup
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run
python manage.py runserver

# Ngrok for WebRTC testing
ngrok http 8000