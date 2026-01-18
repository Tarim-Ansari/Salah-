document.addEventListener("DOMContentLoaded", function() {
    
    // 1. CONFIGURATION
    const STORAGE_KEY = `salah_session_${SESSION_ID}`;

    // 2. DOM ELEMENTS
    const els = {
        timer: document.getElementById("timer"),
        status: document.getElementById("status"),
        deduction: document.getElementById("deduction-amount"),
        rateDisplay: document.getElementById("display-rate"),
        toast: document.getElementById("toast"),
        endBtn: document.getElementById("end-call-btn")
    };

    // Set initial Rate Display
    if(els.rateDisplay) els.rateDisplay.innerText = RATE;

    // 3. STATE
    let state = {
        seconds: 0,
        billingActive: false,
        warningShown: false,
        isPaused: true // Force pause on load
    };

    // Load State (Resume from LocalStorage if reload happened)
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        const parsed = JSON.parse(saved);
        state.seconds = parsed.seconds || 0;
        state.billingActive = parsed.billingActive || false;
        state.warningShown = parsed.warningShown || false;
        
        // We restore time, but we keep isPaused=true until video confirms connection
        state.isPaused = true; 
        updateUI();
    }

    // 4. DAILY VIDEO SETUP
    if (!window.Daily) { alert("Daily Library missing"); return; }

    const call = Daily.createFrame(document.getElementById("video"), {
        showLeaveButton: false,
        iframeStyle: { width: '100%', height: '100%', border: '0', backgroundColor: '#050505' }
    });
    
    if (typeof ROOM_URL !== 'undefined' && ROOM_URL) {
        call.join({ url: ROOM_URL });
    }

    // 5. CORE LOOP (The Heartbeat)
    setInterval(() => {
        if (!state.isPaused) {
            state.seconds++;
            processBilling();
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        }
        updateUI(); 
    }, 1000);

    // 6. EVENTS
    call.on("participant-joined", checkParticipants);
    call.on("participant-left", checkParticipants);
    
    // --- RELOAD HANDLER (Consolidated Logic) ---
    let isPageUnloading = false;

    window.addEventListener("beforeunload", () => {
        // 1. Set flag so we don't show the "Session Ended" alert
        isPageUnloading = true;
        // 2. Force immediate leave so Lawyer gets notified instantly
        if(call) call.leave();
    });

    call.on("left-meeting", () => {
        // Only show the alert if it's a REAL end (clicked button), not a refresh
        if (!isPageUnloading) {
            const cost = calculateCost();
            alert(`Session Ended. Total Estimated Deduction: ₹${cost}`);
            window.location.href = "/client/consultations/"; 
        }
    });

    els.endBtn.addEventListener("click", () => {
        if(confirm("End Consultation?")) call.leave();
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
            els.status.innerText = "Waiting for Expert...";
            els.status.style.color = "#f0a500";
        }
    }

    function processBilling() {
        if (state.seconds <= 120) {
            els.status.innerText = "Free Intro";
            return;
        }

        if (!state.billingActive) {
            state.billingActive = true;
            showToast("Free period over. Billing Started.");
        }

        const currentCost = calculateCost();
        const remaining = BALANCE - currentCost;

        if (remaining < (RATE * 2) && !state.warningShown && remaining > 0) {
            showToast("⚠️ Low Balance Warning");
            state.warningShown = true;
        }

        if (currentCost >= BALANCE) {
            call.leave();
            alert("Balance Exhausted. Ending Call.");
        }
    }

    function calculateCost() {
        const billable = Math.max(0, state.seconds - 120);
        return (billable * (RATE / 60)).toFixed(2);
    }

    function updateUI() {
        const m = String(Math.floor(state.seconds / 60)).padStart(2, "0");
        const s = String(state.seconds % 60).padStart(2, "0");
        els.timer.innerText = `${m}:${s}`;
        els.deduction.innerText = `₹${calculateCost()}`;
    }

    function showToast(msg) {
        els.toast.innerText = msg;
        els.toast.className = "show";
        setTimeout(() => els.toast.className = "", 3000);
    }
});