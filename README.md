
# ⚖️ SALAH 

> **A Pay-Per-Minute Legal Video Consultation Platform**

SALAH is a full-stack web application designed to bridge the gap between clients and legal experts. It transforms the traditional, time-consuming process of booking lawyer appointments into a seamless digital experience. Through real-time video conferencing and a custom "Pay-Per-Minute" wallet system, SALAH guarantees financial transparency for clients and automated, fair compensation for lawyers.

---
## Demo-Video

https://github.com/user-attachments/assets/2b602e2c-2f37-4ef0-ab64-9e1b70671d54



## ✨ Key Features

*   **⏱️ Live Billing Meter (Pay-Per-Minute):** 
    JavaScript-driven live timer that tracks consultation duration. Includes a 2-minute free grace period before initiating per-minute billing.
*   **💳 Integrated Digital Wallet:** 
    A secure virtual ledger utilizing atomic database transactions (`transaction.atomic`) to ensure funds are accurately debited from clients and credited to lawyers without data loss.
*   **📹 Instant Video Rooms:** 
    Integrated with the **Daily.co WebRTC API** to dynamically generate secure, expiring video consultation rooms.
*   **👥 Role-Based Access Control (RBAC):** 
    Distinct authentication flows and customized dashboards for 'Clients' and 'Lawyers'.
*   **📁 Structured Case Briefs:** 
    Clients submit specific case details (Category, Subject, Description) which lawyers can review and Accept/Reject prior to a call.
*   **⭐ Rating & Analytics System:** 
    Post-consultation feedback loop and real-time earnings analytics displayed on the Lawyer's dashboard.

---

## 🛠️ Technology Stack

*   **Backend:** Python, Django (MVT Architecture)
*   **Frontend:** Semantic HTML5, Modern CSS3 (CSS Variables, Flexbox, Grid), Vanilla JavaScript (ES6+)
*   **Database:** SQLite (Development/MVP)
*   **External APIs:** Daily.co REST API (for WebRTC Video Conferencing)
*   **Tools:** Git, GitHub, VS Code, Ngrok (for local HTTPS testing)

---

## 🚀 Installation & Local Setup

Follow these steps to get the project running on your local machine.

### 1. Prerequisites
*   Python 3.x installed on your machine.
*   A free API key from [Daily.co](https://www.daily.co/).

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/SALAH.git
cd SALAH
```

### 3. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate
# Activate it (Mac/Linux)
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install django requests
```

### 5. Configure API Keys
Create .env and add your Daily.co credentials. For reference refer to the .env.example file:
```
DAILY_API_KEY = "your_api_key_here"
DAILY_SUBDOMAIN = "your_subdomain"
SECRET_KEY = "your_secret_key_here"
DEBUG = True
```

### 6. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Optional but recommended)
```bash
python manage.py createsuperuser
```

### 8. Run the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser to view the application.

---

## 🌐 Testing Video Calls Across Devices (Ngrok)

WebRTC (Camera and Microphone access) requires a secure **HTTPS** connection. If you want to test a video call between two different laptops/phones locally:

1. Install [Ngrok](https://ngrok.com/).
2. In `settings.py`, ensure `ALLOWED_HOSTS = ['*']` and add `CSRF_TRUSTED_ORIGINS = ['https://*.ngrok-free.app']`.
3. Run your Django server: `python manage.py runserver`.
4. In a new terminal, start the tunnel: `ngrok http 8000`.
5. Use the generated `https://...ngrok-free.app` link to access the site on your second device.

---

## 👥 Meet the Team

This project was developed collaboratively during the EY GDS Next Gen 4.0 Employability Program.

*   **Abduldiyan** – Backend Developer (Django Architecture, Daily.co API, Wallet/Billing Logic)
*   **Tarim** – Database Administrator (Schema Design, Relational Mapping)
*   **Harshili & Saniya** – Frontend Developers (UI/UX Design, CSS Styling, Responsive Layouts)
*   **Yogesh** – Project Coordinator & QA (Workflow Management, Testing, Presentations)

**Mentorship:** Special thanks to Mr. Vipul Kayate (Master Trainer, EY GDS) for his invaluable guidance.

---

## 📄 License
This project was built for educational and demonstration purposes as an MVP. 
Feel free to explore, fork, and use this codebase as a reference for integrating WebRTC, managing custom wallet ledgers, or building role-based Django applications.

---

## 🗺️ Future Roadmap

While SALAH is currently a fully functional MVP, we have exciting plans for future iterations:

*   **💳 Real Payment Gateways:** Integrate Stripe or Razorpay to transition the virtual wallet into handling real-world transactions and bank payouts.
*   **🤖 AI Legal Assistant:** Add an AI layer to summarize lengthy case briefs and extract key legal statutes before the lawyer reviews the request.
*   **📄 Secure Document Vault:** Implement end-to-end encrypted document sharing for sensitive legal files (PDFs, images) between clients and lawyers.
*   **📱 Mobile Application:** Build dedicated iOS and Android apps using React Native or Flutter for consultations on the go.


*“Justice delayed is justice denied. We built SALAH to make sure neither happens.”* ⚖️



