document.addEventListener("DOMContentLoaded", function() {
    
    // 1. CONFIGURATION
    const STORAGE_KEY = `salah_session_${SESSION_ID}`;

    // 2. DOM ELEMENTS
    const els = {
        timer: document.getElementById("timer"),
        status: document.getElementById("status"),
        endBtn: document.getElementById("end-call-btn")
    };

    // 3. STATE
    let state = {
        seconds: 0,
        isPaused: true // Always start paused to prevent "Lobby Timing" bugs
    };

    // Load State (Sync time from previous session if exists)
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        const parsed = JSON.parse(saved);
        state.seconds = parsed.seconds || 0;
        
        // We restore the TIME, but we force PAUSE until we verify participants
        state.isPaused = true; 
        updateUI();
    }

    // 4. DAILY VIDEO SETUP
    if (!window.Daily) { alert("Daily.co library missing"); return; }

    const call = Daily.createFrame(document.getElementById("video"), {
        showLeaveButton: false,
        iframeStyle: { width: '100%', height: '100%', border: '0', backgroundColor: '#050505' }
    });
    
    if (typeof ROOM_URL !== 'undefined' && ROOM_URL) {
        call.join({ url: ROOM_URL });
    }

    // 5. TIMER LOOP (Runs every second)
    setInterval(() => {
        if (!state.isPaused) {
            state.seconds++;
            
            // --- THE FIX: Lawyer NOW writes to storage ---
            // This ensures if Lawyer reloads, they remember the time.
            // WARNING: Lawyer and Client must be in DIFFERENT BROWSERS (Incognito)
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        }
        updateUI(); 
    }, 1000);

    // 6. EVENTS
    
    // When someone joins, check if we have 2 people
    call.on("participant-joined", checkParticipants);
    
    // STRICT CHECK: When someone leaves, immediately re-count
    call.on("participant-left", () => {
        checkParticipants();
    });

    call.on("left-meeting", () => {
        alert("Session Ended.");
        // Clear storage so next time it starts fresh
        localStorage.removeItem(STORAGE_KEY);
        window.location.href = "/lawyer/consultations/"; 
    });

    els.endBtn.addEventListener("click", () => {
        if(confirm("Are you sure you want to end the session?")) {
            call.leave();
        }
    });

    // 7. HELPER FUNCTIONS
    function checkParticipants() {
        const pCount = Object.keys(call.participants()).length;
        
        // Logic: 2 people = Active. 1 person (just me) = Waiting.
        if (pCount >= 2) {
            state.isPaused = false;
            els.status.innerText = "Live";
            els.status.style.color = "#4ade80"; // Green
        } else {
            state.isPaused = true;
            els.status.innerText = "Waiting for Client...";
            els.status.style.color = "#f0a500"; // Orange
        }
    }

    function updateUI() {
        const m = String(Math.floor(state.seconds / 60)).padStart(2, "0");
        const s = String(state.seconds % 60).padStart(2, "0");
        els.timer.innerText = `${m}:${s}`;
    }
});