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
        isPaused: true
    };

    // Load State (Sync time)
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        const parsed = JSON.parse(saved);
        state.seconds = parsed.seconds || 0;
        updateUI();
    }

    // 4. DAILY VIDEO
    const call = Daily.createFrame(document.getElementById("video"), {
        showLeaveButton: false,
        iframeStyle: { width: '100%', height: '100%', border: '0', backgroundColor: '#050505' }
    });
    
    if (ROOM_URL) call.join({ url: ROOM_URL });

    // 5. TIMER LOOP
    setInterval(() => {
        if (!state.isPaused) {
            state.seconds++;
        }
        updateUI(); 
    }, 1000);

    // 6. EVENTS
    call.on("participant-joined", checkParticipants);
    call.on("participant-left", () => checkParticipants()); // Strict check

    call.on("left-meeting", () => {
        alert("Session Ended.");
        window.location.href = "/lawyer/consultations/"; // Redirect back
    });

    els.endBtn.addEventListener("click", () => {
        if(confirm("End Session?")) call.leave();
    });

    // 7. HELPER FUNCTIONS
    function checkParticipants() {
        const pCount = Object.keys(call.participants()).length;
        if (pCount >= 2) {
            state.isPaused = false;
            els.status.innerText = "Live";
            els.status.style.color = "#4ade80";
        } else {
            state.isPaused = true;
            els.status.innerText = "Waiting for Client...";
            els.status.style.color = "#f0a500";
        }
    }

    function updateUI() {
        const m = String(Math.floor(state.seconds / 60)).padStart(2, "0");
        const s = String(state.seconds % 60).padStart(2, "0");
        els.timer.innerText = `${m}:${s}`;
    }
});