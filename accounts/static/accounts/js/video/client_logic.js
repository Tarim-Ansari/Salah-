document.addEventListener("DOMContentLoaded", function() {
    
    // 1. CONFIGURATION (Read from Global Variables set in HTML)
    // We no longer read from URL. We read from Django passed variables.
    const STORAGE_KEY = `salah_session_${SESSION_ID}`;

    // 2. DOM ELEMENTS
    const els = {
        timer: document.getElementById("timer"),
        status: document.getElementById("status"),
        deduction: document.getElementById("deduction-amount"),
        rateDisplay: document.getElementById("display-rate"),
        costWrapper: document.getElementById("cost-wrapper"),
        toggleBtn: document.getElementById("toggle-btn"),
        toast: document.getElementById("toast"),
        endBtn: document.getElementById("end-call-btn")
    };

    if(els.rateDisplay) els.rateDisplay.innerText = RATE;

    // 3. STATE
    let state = {
        seconds: 0,
        billingActive: false,
        warningShown: false,
        isPaused: true // Force pause on load
    };

    // Load State (Time only)
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        const parsed = JSON.parse(saved);
        state.seconds = parsed.seconds || 0;
        state.billingActive = parsed.billingActive || false;
        state.warningShown = parsed.warningShown || false;
        state.isPaused = true; 
        updateUI();
    }

    // 4. DAILY VIDEO
    if (!window.Daily) { alert("Daily Library missing"); return; }

    const call = Daily.createFrame(document.getElementById("video"), {
        showLeaveButton: false,
        iframeStyle: { width: '100%', height: '100%', border: '0', backgroundColor: '#050505' }
    });
    
    if (ROOM_URL) {
        call.join({ url: ROOM_URL });
    }

    // 5. CORE LOOP
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
    
    call.on("left-meeting", () => {
        const cost = calculateCost();
        // Here we will eventually send this data to the backend
        alert(`Session Ended. Total Deduction: ₹${cost}`);
        window.location.href = "/client/consultations/"; // Redirect back to list
    });

    els.endBtn.addEventListener("click", () => {
        if(confirm("End Consultation?")) call.leave();
    });

    // Toggle Blur
    let isBlurVisible = false;
    els.toggleBtn.addEventListener("click", () => {
        if (isBlurVisible) {
            els.costWrapper.classList.add('blurred');
            els.costWrapper.classList.remove('unblurred');
            els.toggleBtn.innerText = "👁️"; 
        } else {
            els.costWrapper.classList.remove('blurred');
            els.costWrapper.classList.add('unblurred');
            els.toggleBtn.innerText = "❌"; 
        }
        isBlurVisible = !isBlurVisible;
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
            showToast("Billing Started");
        }
        const currentCost = calculateCost();
        const remaining = BALANCE - currentCost;

        if (remaining < (RATE * 2) && !state.warningShown && remaining > 0) {
            showToast("⚠️ Low Balance");
            state.warningShown = true;
        }
        if (currentCost >= BALANCE) {
            call.leave();
            alert("Balance Exhausted");
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