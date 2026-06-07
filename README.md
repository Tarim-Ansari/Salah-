# ⚖️ SALAH - AI-Powered Legal Consultation Platform

> **Pay-Per-Minute Video Consultations with AI Transcription & Smart Assistance**

SALAH revolutionizes legal consultations by combining real-time video conferencing, transparent pay-per-minute billing, and AI-powered transcription. This platform bridges the gap between clients seeking justice and legal experts, making legal advice accessible, affordable, and transparent.

---

## 🎥 Demo Video

https://github.com/user-attachments/assets/2b602e2c-2f37-4ef0-ab64-9e1b70671d54

---

## ✨ Key Features

### 💰 **Smart Billing System**
- **Pay-Per-Minute:** ₹20/minute billing with 2-minute grace period
- **Live Meter:** Real-time cost display during consultation
- **Integrated Wallet:** Secure virtual wallet with atomic transactions
- **Auto-Cutoff:** Call ends automatically when wallet balance depletes

### 🎙️ **AI-Powered Transcription (NEW!)**
- **Y-Splitter Recording:** Browser-based audio capture (no cloud recording fees)
- **Groq Whisper AI:** 100% free, highly accurate transcription
- **Dual Recording:** Both client and lawyer audio captured separately
- **Speaker Labels:** Transcript shows `[CLIENT]` and `[LAWYER]` tags
- **Smart UI:** Compact transcript display with expand/collapse

### 🤖 **AI Legal Assistant**
- **Pre-Call Analysis:** AI refines case descriptions before lawyer review
- **Smart Checklist:** AI generates personalized questions for clients
- **Cost Estimation:** AI predicts consultation duration and cost
- **Post-Call Summary:** AI summarizes key points from transcript

### 📹 **Video Consultation**
- **Daily.co Integration:** Secure, expiring video rooms
- **Instant Join:** One-click access for both parties
- **Mute Sync:** Recording pauses when user mutes
- **Mobile Friendly:** Works on desktop and mobile browsers

### 🎨 **Modern UI/UX**
- **Smooth Animations:** 406-line CSS animation library
- **Responsive Design:** Works on all screen sizes
- **Dark Theme:** Professional, eye-friendly interface
- **Intuitive Navigation:** Role-based dashboards

---

## 🛠️ Technology Stack

### Backend
- **Framework:** Django 4.x (Python 3.x)
- **Database:** SQLite (Development) / PostgreSQL (Production-ready)
- **APIs:** Daily.co (WebRTC), Groq (AI Transcription)

### Frontend
- **HTML5:** Semantic markup
- **CSS3:** Custom animations, Flexbox, Grid
- **JavaScript:** ES6+, Vanilla JS (no frameworks)

### AI & ML
- **Groq Whisper:** Audio transcription
- **Groq Llama 3:** Case analysis and summarization

---

## 🚀 Complete Setup Guide (For Judges/Evaluators)

### Prerequisites

Before starting, ensure you have:
- ✅ Python 3.8 or higher
- ✅ Git installed
- ✅ A code editor (VS Code recommended)
- ✅ Modern browser (Chrome, Edge, or Firefox)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Omnisslayer01/Salah-online.git
cd Salah-online
```

### Step 2: Set Up Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- Django 4.x
- requests (for Daily.co API)
- groq (for AI transcription)
- python-dotenv (for environment variables)

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Daily.co API (for video calls)
DAILY_API_KEY=your-daily-api-key
DAILY_SUBDOMAIN=your-subdomain

# Groq AI API (for transcription)
GROQ_API_KEY=your-groq-api-key
```

**How to get API keys:**

1. **Daily.co API Key:**
   - Visit https://www.daily.co/
   - Sign up for free account
   - Go to Developers → API Keys
   - Copy your API key and subdomain

2. **Groq API Key:**
   - Visit https://console.groq.com/
   - Sign up for free account
   - Go to API Keys section
   - Create new API key

**Example `.env` file:**
```env
SECRET_KEY=django-insecure-your-secret-key-123456
DEBUG=True
DAILY_API_KEY=abc123def456ghi789
DAILY_SUBDOMAIN=salah-demo
GROQ_API_KEY=gsk_xyz789abc123def456
```

### Step 5: Database Setup

```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Create admin user (optional but recommended)
python manage.py createsuperuser
```

**When creating superuser:**
- Username: `admin`
- Email: `admin@salah.com`
- Password: (choose a secure password)

### Step 6: Run the Development Server

```bash
python manage.py runserver
```

**You should see:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Step 7: Access the Application

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 👥 Testing the Complete Flow

### Quick Test Scenario (5 minutes)

**1. Create Two User Accounts:**

**Client Account:**
- Go to http://127.0.0.1:8000
- Click "Signup"
- Select role: **Client**
- Email: `client@test.com`
- Password: `test123`

**Lawyer Account:**
- Open **incognito/private window**
- Go to http://127.0.0.1:8000
- Click "Signup"
- Select role: **Lawyer**
- Email: `lawyer@test.com`
- Password: `test123`
- Upload profile photo (optional)

**2. Add Funds to Client Wallet:**
- Login as client
- Click "Wallet" in navigation
- Click "Add Funds"
- Enter amount: `500` (₹500)
- Click "Add Funds"

**3. Request Consultation:**
- As client, go to "Experts"
- Find the lawyer you created
- Click "Request Consultation"
- Fill in case details:
  - Category: "Family Law"
  - Subject: "Property dispute"
  - Description: "I need help with a property inheritance issue"
- Click "Submit Request"
- **Wait 5-10 seconds** for AI to analyze (you'll see a loading spinner)

**4. Accept Consultation (Lawyer Side):**
- Switch to lawyer's incognito window
- Go to "Consultations"
- You'll see the pending request
- Click "Accept"

**5. Start Video Call:**
- **Client:** Go to "My Consultations" → Click "Join Video Call"
- **Lawyer:** Go to "Consultations" → Click "Start Video Call"
- **Allow microphone and camera** when browser asks

**6. During the Call:**
- **Speak clearly** for 10-15 seconds (e.g., "This is a test of the audio recording system")
- **Check browser console** (F12) to see recording logs:
  ```
  🎙️ Y-SPLITTER ACTIVE
  📦 Audio chunk received: 4096 bytes
  ```
- **Try muting/unmuting** to test sync
- **Watch the billing meter** count up

**7. End the Call:**
- Click "Leave" button
- **Wait 5 seconds** for audio to upload
- Check console for: `✅ Audio uploaded successfully`

**8. View Transcript:**
- Go to "My Consultations" (client) or "Consultations" (lawyer)
- **Refresh the page** (Ctrl+Shift+R)
- You should see: `📝 Call Transcript & Summary`
- Click to expand and view the transcript

---

## 🔍 Troubleshooting

### Issue: "No module named 'groq'"
**Solution:**
```bash
pip install groq
```

### Issue: "Bad Request: /api/process-audio/"
**Solution:**
- Check `.env` file has `GROQ_API_KEY`
- Restart Django server: `Ctrl+C` then `python manage.py runserver`

### Issue: Video call not connecting
**Solution:**
- Check `.env` file has `DAILY_API_KEY` and `DAILY_SUBDOMAIN`
- Ensure you're using HTTPS (or localhost)
- Try different browser (Chrome recommended)

### Issue: Microphone permission denied
**Solution:**
- Click address bar lock icon
- Go to "Site settings"
- Set Microphone to "Allow"
- Refresh page

### Issue: Transcript not appearing
**Solution:**
- Wait 10 seconds after call ends
- Hard refresh page (Ctrl+Shift+R)
- Check Django console for errors
- Verify `GROQ_API_KEY` is valid

---

## 🌐 Testing Across Multiple Devices

To test video calls between two different computers/phones:

### Option 1: Ngrok (Recommended)

1. **Install Ngrok:**
   - Download from https://ngrok.com/
   - Extract and add to PATH

2. **Update Django Settings:**
   ```python
   # In core/settings.py
   ALLOWED_HOSTS = ['*']
   CSRF_TRUSTED_ORIGINS = ['https://*.ngrok-free.app']
   ```

3. **Start Django Server:**
   ```bash
   python manage.py runserver
   ```

4. **Start Ngrok Tunnel:**
   ```bash
   ngrok http 8000
   ```

5. **Use the HTTPS URL:**
   - Ngrok will show: `https://abc123.ngrok-free.app`
   - Use this URL on both devices

### Option 2: Local Network

1. **Find your IP address:**
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig`

2. **Update settings:**
   ```python
   ALLOWED_HOSTS = ['*']
   ```

3. **Access from other device:**
   ```
   http://YOUR_IP_ADDRESS:8000
   ```

---

## 📊 Project Structure

```
Salah-online/
├── accounts/                    # Main Django app
│   ├── models.py               # Database models (User, Wallet, Consultation)
│   ├── views.py                # Business logic & API endpoints
│   ├── urls.py                 # URL routing
│   ├── static/
│   │   └── accounts/
│   │       ├── css/
│   │       │   ├── style.css           # Main styles
│   │       │   └── animations.css      # Animation library (406 lines)
│   │       └── js/
│   │           └── video/
│   │               ├── client_logic.js  # Client-side recording
│   │               └── lawyer_logic.js  # Lawyer-side recording
│   └── templates/              # HTML templates
│       └── accounts/
│           ├── client/         # Client pages
│           ├── lawyer/         # Lawyer pages
│           └── video/          # Video call pages
├── core/                       # Django project settings
│   ├── settings.py            # Configuration
│   └── urls.py                # Root URL config
├── media/                      # Uploaded files (profile photos)
├── .env                        # Environment variables (create this)
├── .env.example               # Example environment file
├── requirements.txt           # Python dependencies
├── manage.py                  # Django management script
└── README.md                  # This file
```

---

## 🎯 Key Features Demonstration

### 1. AI Case Analysis
- Submit a consultation request
- Watch AI refine the description
- See estimated cost and duration
- View personalized checklist

### 2. Live Billing
- Start a video call
- Watch the meter count: ₹0.00 → ₹20.00 → ₹40.00
- See wallet balance decrease in real-time
- Call auto-ends when balance reaches zero

### 3. Audio Transcription
- Speak during the call
- End the call
- Refresh consultations page
- View transcript with speaker labels

### 4. Smooth Animations
- Navigate between pages
- Hover over buttons and cards
- Watch fade-in effects
- Experience smooth transitions

---

## 👥 Team

**Developed for Rhett Hackathon by:**

- **Abduldiyan Irfan Deshmukh** – Full-Stack Developer (Django, Daily.co, AI Integration)
- **Tarim** – Database Architect (Schema Design, Optimization)
- **Harshili & Saniya** – Frontend Developers (UI/UX, Responsive Design)
- **Yogesh** – Project Manager & QA (Testing, Documentation)

**Mentorship:** Mr. Vipul Kayate (Master Trainer, EY GDS)

---

## 📄 License

This project is built for educational and demonstration purposes. Feel free to explore, fork, and use as a reference for:
- WebRTC video integration
- AI transcription systems
- Custom wallet/billing logic
- Role-based Django applications

---

## 🗺️ Future Roadmap

### Phase 1 (Current - Hackathon MVP)
- ✅ Video consultations
- ✅ Pay-per-minute billing
- ✅ AI transcription
- ✅ Case analysis

### Phase 2 (Post-Hackathon)
- 💳 Real payment gateways (Stripe/Razorpay)
- 📱 Mobile apps (React Native)
- 🔒 End-to-end encryption
- 🌍 Multi-language support

### Phase 3 (Scale)
- 🤖 Advanced AI legal assistant
- 📄 Document generation
- 📊 Analytics dashboard
- 🔗 Court filing integration

---

## 📞 Support

For questions or issues during evaluation:
- **Email:** abduldiyan@example.com
- **GitHub Issues:** https://github.com/Omnisslayer01/Salah-online/issues
- **Documentation:** See `AUDIO_RECORDING_TEST_CHECKLIST.md` for detailed testing guide

---

## 🏆 Hackathon Highlights

**What Makes SALAH Special:**

1. **Cost Innovation:** Y-Splitter recording saves 100% on cloud recording fees
2. **AI Integration:** Groq Whisper provides free, accurate transcription
3. **User Experience:** Smooth animations and intuitive interface
4. **Transparency:** Real-time billing with no hidden costs
5. **Accessibility:** Makes legal advice affordable for everyone

---

*"Justice delayed is justice denied. We built SALAH to make sure neither happens."* ⚖️

**Built with ❤️ for Rhett Hackathon 2026**
