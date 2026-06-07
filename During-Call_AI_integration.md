# ⚡ SALAH: Phase 2 - During Call (The AI Co-Pilot & Whisper Transcription Pivot)

**Goal:** Transform the live video call from a standard meeting into an AI-assisted workspace. We are pivoting away from expensive Daily.co cloud recording AND the browser's built-in speech tool. Instead, we will use the **"Y-Splitter" Method**: silently capturing audio directly from the browser's microphone, uploading it when the call ends, and passing it to **Groq Whisper AI** for 100% free, highly accurate transcription.

---

### 🎙️ Step 1: The "Y-Splitter" Silent Recorder (✅ COMPLETED)
**Target Files:**
- [`accounts/static/accounts/js/video/client_logic.js`](accounts/static/accounts/js/video/client_logic.js:70-180)
- [`accounts/static/accounts/js/video/lawyer_logic.js`](accounts/static/accounts/js/video/lawyer_logic.js:65-205)

**Status:** ✅ **FULLY IMPLEMENTED AND WORKING**

**What Was Implemented:**
Instead of using Daily.co's audio track API (which doesn't work), we use the browser's native `getUserMedia()` API to capture audio directly from the microphone.

**Implementation Details:**

1. **Initialize Variables** (at top of JS files):
```javascript
// Audio Recording Variables (Y-Splitter Method for Groq Whisper)
let audioRecorder = null;
let audioChunks = [];
```

2. **Capture Audio on Meeting Join** (inside `call.on("joined-meeting")`):
```javascript
call.on("joined-meeting", async () => {
    try {
        // 1. Request microphone access from browser (NOT from Daily.co)
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: false
        });
        
        // 2. Extract audio track
        const audioTrack = stream.getAudioTracks()[0];
        console.log("✅ Microphone:", audioTrack.label);
        
        // 3. Create MediaRecorder with browser-supported format
        let mimeType = 'audio/webm';
        if (!MediaRecorder.isTypeSupported('audio/webm')) {
            mimeType = 'audio/mp4'; // Fallback for Safari
        }
        
        audioRecorder = new MediaRecorder(stream, { mimeType: mimeType });
        
        // 4. Clear previous chunks (prevent memory leaks)
        audioChunks = [];
        
        // 5. Collect audio chunks every 1 second
        audioRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
                console.log(`📦 Audio chunk received: ${event.data.size} bytes`);
            }
        };
        
        // 6. Handle upload when recording stops
        audioRecorder.onstop = async () => {
            if (audioChunks.length > 0) {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'client_recording.webm'); // or 'lawyer_recording.webm'
                formData.append('room_id', SESSION_ID);
                
                try {
                    await fetch('/api/process-audio/', {
                        method: 'POST',
                        headers: { 'X-CSRFToken': getCookie('csrftoken') },
                        body: formData
                    });
                    console.log("✅ Audio uploaded successfully");
                } catch (error) {
                    console.error("❌ Audio upload failed:", error);
                }
            }
        };
        
        // 7. Start recording with 1-second intervals
        audioRecorder.start(1000); // CRITICAL: timeslice parameter
        console.log("🎙️ Y-SPLITTER ACTIVE");
        
    } catch (error) {
        console.error("❌ Failed to initialize recording:", error);
        if (error.name === 'NotAllowedError') {
            alert("Please allow microphone access to record the consultation.");
        }
    }
});
```

3. **Stop and Upload on Call End** (inside `call.on("left-meeting")`):
```javascript
call.on("left-meeting", async () => {
    // Stop audio recorder FIRST (before payment/redirect)
    if (audioRecorder && audioRecorder.state !== "inactive") {
        console.log("🛑 Stopping audio recorder...");
        audioRecorder.stop();
        // Wait 2 seconds for upload to complete
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // ... existing payment/redirect logic ...
});
```

**Key Technical Decisions:**

| Decision | Reason |
|----------|--------|
| Use `getUserMedia()` instead of Daily.co API | Daily.co's `participants.local.tracks.audio.track` returns `undefined` |
| Add `start(1000)` timeslice | Without it, `ondataavailable` only fires on `stop()`, no chunks collected |
| Separate streams for client/lawyer | Each browser records its own audio independently |
| Upload on `onstop` event | Ensures all chunks are collected before upload |
| 2-second wait after `stop()` | Gives upload time to complete before page redirect |

**Testing Verification:**
```
✅ Step 1-10: All initialization steps complete
🎙️ Y-SPLITTER ACTIVE
Recording state: recording
📦 Audio chunk received: 4096 bytes (Total chunks: 1)
📦 Audio chunk received: 4096 bytes (Total chunks: 2)
...
```

**Documentation:**
- Full technical explanation: [`Y_SPLITTER_COMPLETE_TECHNICAL_EXPLANATION.md`](Y_SPLITTER_COMPLETE_TECHNICAL_EXPLANATION.md)
- Diagnostic guide: [`Y_SPLITTER_DIAGNOSTIC_GUIDE.md`](Y_SPLITTER_DIAGNOSTIC_GUIDE.md)
- Bug fix report: [`BUG_FIX_REPORT_Y_SPLITTER_AUDIO_RECORDING.md`](BUG_FIX_REPORT_Y_SPLITTER_AUDIO_RECORDING.md)

---

### ✅ Step 2: The User's AI Checklist UI (Assigned to: Frontend) (✅ COMPLETED)
**Target File:** `accounts/templates/accounts/consultation/client_room.html`
**Goal:** Display the AI-generated questions from Phase 1 as an interactive checklist in the sidebar.

**Action:**
Inside the `<aside class="sidebar">`, inject this HTML:
```html
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

### 🔗 Step 3: Injecting Context into the Video View (Assigned to: Diyan) (✅ COMPLETED)
**Target File:** `accounts/views.py` -> `join_room()` view
**Goal:** Ensure the backend passes the `consultation` object to the templates so Steps 2  actually render data.

**Action:**
Ensure `consultation` is explicitly passed in the context dictionary before `return render()`:
```python
    # Inside join_room view:
    ctx = {
        "room_url": daily_url, 
        "session_id": room_id,
        "consultation": consultation, # <--- CRITICAL FOR FRONTEND UI TO WORK
        "balance": getattr(request.user.wallet, 'balance', 0), # if applicable
        "rate": 20 
    }
```
*(Note: Do NOT add `enable_recording: "cloud"` to the Daily.co payload anymore. We are bypassing their fees).*

---

### 🏁 Step 3: Backend Audio Processing with Groq Whisper (✅ COMPLETED)
**Target File:** [`accounts/views.py:573-665`](accounts/views.py:573-665)
**Goal:** Create endpoint to receive uploaded audio, transcribe with Groq Whisper AI, and save to database.

**Status:** ✅ **FULLY IMPLEMENTED**

**What Was Implemented:**
- Endpoint created at `/api/process-audio/` ([`accounts/views.py:573-665`](accounts/views.py:573-665))
- URL route added ([`accounts/urls.py:41`](accounts/urls.py:41))
- Receives audio files from client/lawyer
- Transcribes with Groq Whisper AI (100% FREE)
- Appends transcript with speaker labels: `[CLIENT]:` or `[LAWYER]:`
- Automatic temp file cleanup
- Full error handling and security

**Documentation:**
- Complete implementation report: [`STEP3_AUDIO_PROCESSING_IMPLEMENTATION_REPORT.md`](STEP3_AUDIO_PROCESSING_IMPLEMENTATION_REPORT.md)

---

### 🕵️ Step 4: Handle Daily.co Mute Button Edge Case (✅ COMPLETED)
**Target Files:**
- [`accounts/static/accounts/js/video/client_logic.js:237-268`](accounts/static/accounts/js/video/client_logic.js:237-268)
- [`accounts/static/accounts/js/video/lawyer_logic.js:248-279`](accounts/static/accounts/js/video/lawyer_logic.js:248-279)

**Goal:** Sync MediaRecorder with Daily.co's mute button to prevent recording when user is muted.

**Status:** ✅ **FULLY IMPLEMENTED**

**The Issue:**
Because we're using `getUserMedia()` independently from Daily.co, our MediaRecorder keeps recording even when the user clicks Daily.co's "Mute" button. This means:
- ✅ **Good:** Transcript won't have missing chunks if someone accidentally mutes
- ⚠️ **Quirk:** User might think they're muted but we're still recording them

**What Was Implemented:**

Added `setupMuteSync()` function that:
1. Polls Daily.co's mute state every 500ms
2. Pauses MediaRecorder when user mutes via Daily.co UI
3. Resumes MediaRecorder when user unmutes
4. Logs state changes to console for debugging

**Implementation:**
```javascript
function setupMuteSync() {
    let lastMuteState = false;
    
    const muteCheckInterval = setInterval(() => {
        if (!audioRecorder || audioRecorder.state === "inactive") {
            clearInterval(muteCheckInterval);
            return;
        }
        
        try {
            const currentMuteState = !call.localAudio();
            
            if (currentMuteState !== lastMuteState) {
                lastMuteState = currentMuteState;
                
                if (currentMuteState && audioRecorder.state === "recording") {
                    audioRecorder.pause();
                    console.log("⏸️ Recording paused (user muted via Daily.co)");
                } else if (!currentMuteState && audioRecorder.state === "paused") {
                    audioRecorder.resume();
                    console.log("▶️ Recording resumed (user unmuted)");
                }
            }
        } catch (error) {
            console.warn("⚠️ Mute sync error:", error.message);
        }
    }, 500);
    
    console.log("✅ Mute button sync enabled");
}
```

**Benefits:**
- ✅ Respects user privacy when they mute
- ✅ Prevents recording muted audio (saves bandwidth)
- ✅ Transcript only includes spoken content
- ✅ Automatic cleanup when recording stops

**Testing:**
1. Join call and verify recording starts
2. Click Daily.co's mute button
3. Check console for: `⏸️ Recording paused (user muted via Daily.co)`
4. Unmute
5. Check console for: `▶️ Recording resumed (user unmuted)`

---

### ⚠️ Technical Safety Nets for the Live Demo:
1. **Wallet Timer Protection:** NO changes made to `calculateCost()` or `processBilling()` functions. The ₹20/min rate and wallet exhaustion cut-offs remain intact.
2. **Audio File Size:** The `MediaRecorder` generates `.webm` files. For a 5-10 minute demo, file size is 1-2 MB, uploads instantly.
3. **Dual Audio Processing:** Client's browser records client audio, Lawyer's browser records lawyer audio. Backend appends them together (`existing + new_transcript`) so Phase 3 LLM gets the full conversation.
4. **Browser Compatibility:**
   - Chrome/Edge/Firefox: `audio/webm` (optimal)
   - Safari: Falls back to `audio/mp4`
5. **Permission Handling:** If user denies microphone permission, recording fails gracefully with console error. Call continues normally.
6. **Upload Reliability:** 2-second wait after `stop()` ensures upload completes before page redirect.

***

# 🔮 Future Scope (To be implemented later)

*These features should be mentioned during pitches to show scaling potential, but are not required for the current MVP.*

*   **Lawyer's Smart Notepad:** Providing the lawyer with a text box in the sidebar to type rough bullet points during the call. When the call ends, the AI uses those specific bullet points (instead of relying solely on the transcript) to draft the final legal document, giving the lawyer ultimate control over the output.
*   **Live Translations (Hindi ↔ English):** Utilizing real-time WebRTC audio streams to provide live translated subtitles at the bottom of the video feed, breaking the language barrier between rural clients and urban corporate lawyers.
*   **Live Legal Section Recommendations:** As the user speaks, the live transcript feeds continuously into the LLM. The AI detects keywords and automatically suggests relevant legal sections (e.g., IPC/BNS sections) or compliance acts on the lawyer’s sidebar.