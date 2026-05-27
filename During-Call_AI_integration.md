# ⚡ SALAH: Phase 2 - During Call (The AI Co-Pilot) Implementation Guide

**Goal:** Transform the live video call from a standard meeting into an AI-assisted workspace. We will inject the Phase 1 AI data directly into the video room sidebars, empowering the Client with a checklist and the Lawyer with instant context, while setting up cloud transcription for Phase 3.

---

### 🎙️ Step 1: Enable Cloud Transcription (Assigned to: Diyan)
**Target File:** `accounts/views.py`
**Goal:** Modify the Daily.co API call to automatically record and transcribe the session. If this isn't done, the Phase 3 Summary won't have any audio data to process.

**Action:**
Locate the `join_room` view. Update the `requests.post` payload to include Daily's recording features:
```python
@login_required
def join_room(request, room_id):
    consultation = get_object_or_404(ConsultationRequest, room_id=room_id)
    # ... security checks ...

    # Update this payload
    try:
        requests.post(
            "https://api.daily.co/v1/rooms",
            headers={"Authorization": f"Bearer {settings.DAILY_API_KEY}"},
            json={
                "name": room_id,
                "properties": {
                    "enable_chat": True,
                    "start_video_off": False,
                    "start_audio_off": False,
                    "exp": int(time.time() + 7200),
                    # NEW TRANSCRIPTION PARAMS
                    "enable_recording": "cloud",
                    "enable_transcription": True 
                }
            }
        )
    except: pass

    # ... Ensure 'consultation' is passed in the context for Step 2 & 3
    if request.user == consultation.lawyer:
        return render(request, "accounts/consultation/lawyer_room.html", {
            "room_url": daily_url, "session_id": room_id, "consultation": consultation
        })
    else:
        return render(request, "accounts/consultation/client_room.html", {
            "room_url": daily_url, "session_id": room_id, "balance": request.user.wallet.balance, "rate": 20, "consultation": consultation
        })
```

---

### ✅ Step 2: The User's AI Checklist UI (Assigned to: Frontend / Harshili & Saniya)
**Target File:** `accounts/templates/accounts/consultation/client_room.html`
**Goal:** Utilize the existing sidebar to display the AI-generated questions. As the user asks them, they can check them off.

**Action:**
Inside the `<aside class="sidebar">`, right below the "Total Bill" `metric-card`, inject the interactive checklist:
```html
<!-- Add this under the Total Bill card in the Sidebar -->
<div class="metric-card" style="margin-top: 15px; border-left: 3px solid #2ecc71;">
    <div style="color: #2ecc71; font-weight: bold; margin-bottom: 10px;">AI Checklist</div>
    <div id="ai-checklist" style="font-size: 0.85rem; color: #ccc;">
        {% if consultation.ai_client_checklist %}
            {% for question in consultation.ai_client_checklist %}
                <label style="display: flex; gap: 8px; margin-bottom: 8px; cursor: pointer;">
                    <input type="checkbox" style="accent-color: #d89c3a;"> 
                    <span>{{ question }}</span>
                </label>
            {% endfor %}
        {% else %}
            <p>No checklist generated.</p>
        {% endif %}
    </div>
</div>
```

---

### ⚖️ Step 3: The Lawyer's Context UI (Assigned to: Frontend / Harshili & Saniya)
**Target File:** `accounts/templates/accounts/consultation/lawyer_room.html`
**Goal:** Display the AI Case Brief in the lawyer's sidebar so they don't have to ask "Why are you here today?"

**Action:**
Inside the `<aside class="sidebar">`, right above the "End Session" button, add the case brief:
```html
<!-- Add this to the Lawyer's Sidebar -->
<div class="metric-card" style="margin-top: 15px; border-left: 3px solid #d89c3a; max-height: 250px; overflow-y: auto;">
    <div style="color: #d89c3a; font-weight: bold; margin-bottom: 10px;">Case Context</div>
    <div style="font-size: 0.85rem; color: #ddd; line-height: 1.5;">
        {{ consultation.ai_refined_description|default:consultation.description }}
    </div>
</div>
```

---

### ⏱️ Step 4: Protect the Existing Wallet Timer (Assigned to: Yogesh / QA)
**Target File:** `accounts/static/accounts/js/video/client_logic.js`
**Goal:** Ensure the new UI changes do not break the 2-minute free grace period and the Pay-Per-Minute API trigger.

**Action:**
*   **DO NOT** alter the `calculateCost()` or `processBilling()` functions. They already perfectly handle the ₹20/min rate and wallet exhaustion cut-offs.
*   The Daily.co iframe (`call.join({ url: ROOM_URL })`) is already properly embedded via the JS. Just ensure the parent containers in the HTML still have `id="video"`.

---

### 🏁 Step 5: Preparing the "End Call" Transition for Phase 3 (Assigned to: Diyan)
**Target File:** `client_logic.js`
**Goal:** Currently, when the call ends, the user is redirected to `/client/consultations/`. We need to route them to a new "Summary Processing" page where Phase 3 will happen.

**Action:**
In `client_logic.js`, locate the `call.on("left-meeting", async () => { ... })` block.
Change the success redirect from this:
`window.location.href = "/client/consultations/";`
To this:
`window.location.href = "/consultation/" + SESSION_ID + "/summary/";`

*(Note: Diyan will need to create this `/summary/` view and URL path for Phase 3).*

---

### 🚨 Missing Piece 1: Auto-Starting the Recording (Assigned to: Frontend/Yogesh)
**The Problem:** In Step 1, we *enabled* recording and transcription in the backend. But Daily.co does not start recording automatically just because it's enabled. Someone has to press the "Record" button, OR we have to trigger it in the code.
**Target File:** `accounts/static/accounts/js/video/lawyer_logic.js`
**Action:** We should make the Lawyer the "Host" who automatically triggers the recording as soon as they join. Add this to the `call.on("joined-meeting")` event in `lawyer_logic.js`:
```javascript
call.on("joined-meeting", () => {
    // Silently start recording and transcription in the background
    call.startRecording();
    call.startTranscription();
});
```

### 🚨 Missing Piece 2: The Rating Modal Redirect Bug (Assigned to: Diyan/Frontend)
**The Problem:** In Step 5, I told you to change the `window.location.href` to route to the new `/summary/` page when the call ends. **BUT**, if the payment is successful, the code currently pops up the **Rating Modal**. If you look at your current `client_logic.js`, the `submitRating` and `skipRating` functions *also* have hardcoded redirects to `/client/consultations/`. If we don't change those, the user rates the lawyer and then entirely misses the Phase 3 summary!
**Target File:** `accounts/static/accounts/js/video/client_logic.js`
**Action:** Find `window.submitRating` and `window.skipRating` at the bottom of the file and update their redirects:
```javascript
    window.submitRating = async function() {
        // ... existing fetch code ...
        // CHANGE THIS LINE:
        window.location.href = "/consultation/" + SESSION_ID + "/summary/"; 
    };

    window.skipRating = function() {
        // CHANGE THIS LINE:
        window.location.href = "/consultation/" + SESSION_ID + "/summary/"; 
    };
```

### 🚨 Missing Piece 3: Passing the Consultation to the Template Context (Assigned to: Diyan)
**The Problem:** In Steps 2 & 3, we injected `{{ consultation.ai_client_checklist }}` into the HTML. But your current `join_room` view in `views.py` only passes `"room_url"` and `"session_id"` to the template. It doesn't pass the `consultation` object!
**Target File:** `accounts/views.py` (Inside `join_room`)
**Action:** Make sure you explicitly add the consultation object to the `ctx` dictionary before calling `return render`:
```python
    # Find this part in your join_room view
    ctx = {
        "room_url": daily_url, 
        "session_id": room_id,
        "consultation": consultation  # <--- THIS IS REQUIRED FOR THE UI TO WORK!
    }
```

***

### ⚠️ Technical Safety Nets for the Live Demo:
1. **Daily.co Transcription Tier:** Ensure your Daily.co account tier allows cloud recording/transcription. If it is disabled on the free tier, the API call in Step 1 might return a 400 error. Test this immediately.
2. **iframe Permissions:** Browsers are very strict. Ensure your Ngrok tunnel is running on **HTTPS**. If it's HTTP, Chrome will block the camera and microphone inside the Daily.co iframe.

***

# 🔮 Future Scope (Phase 2 Additions)

*These are advanced features to be mentioned during pitches and startup presentations to show the platform's scaling potential. Do not implement these for the MVP demo to maintain stability.*

*   **Live Translations (Hindi ↔ English):** Utilizing real-time WebRTC audio streams to provide live translated subtitles at the bottom of the video feed, breaking the language barrier between rural clients and urban corporate lawyers.
*   **Live Legal Section Recommendations:** As the user speaks, the live transcript feeds continuously into the LLM. The AI detects keywords and automatically suggests relevant legal sections (e.g., IPC/BNS sections) or compliance acts on the lawyer’s sidebar.
*   **Real-Time Simplified Explanations:** When the lawyer utilizes complex legal jargon, the AI detects it and instantly generates a "layman's terms" definition on the client's sidebar (e.g., Lawyer says "Habeas Corpus," UI shows "A legal action to seek relief from unlawful detention").
*   **WebRTC Custom Pipeline:** Moving away from Daily.co's pre-built frame and using raw WebRTC + WebSockets to process audio chunks directly through a custom Speech-to-Text engine for ultra-low latency processing.


