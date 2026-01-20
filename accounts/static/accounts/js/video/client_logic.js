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
        endBtn: document.getElementById("end-call-btn"),
        ratingModal: document.getElementById("rating-modal")
    };

    if(els.rateDisplay) els.rateDisplay.innerText = RATE;

    // 3. STATE
    let state = {
        seconds: 0,
        billingActive: false,
        warningShown: false,
        isPaused: true
    };

    // Load State
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        const parsed = JSON.parse(saved);
        state.seconds = parsed.seconds || 0;
        state.billingActive = parsed.billingActive || false;
        state.warningShown = parsed.warningShown || false;
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
    
    // RELOAD HANDLER
    let isPageUnloading = false;
    window.addEventListener("beforeunload", () => {
        isPageUnloading = true;
        if(call) call.leave();
    });

    // --- LEFT MEETING (PAYMENT + MODAL TRIGGER) ---
    call.on("left-meeting", async () => {
        if (!isPageUnloading) {
            const cost = calculateCost();
            let paymentSuccess = false;
            
            // 1. Process Payment
            if (cost > 0) {
                els.status.innerText = "Processing Payment...";
                try {
                    const response = await fetch("/api/end_consultation/", {
                        method: "POST",
                        headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
                        body: JSON.stringify({ room_id: SESSION_ID, amount: cost })
                    });
                    const result = await response.json();
                    if (result.status === "success") paymentSuccess = true;
                } catch (error) {
                    console.error("Payment Error:", error);
                }
            } else {
                paymentSuccess = true; // Free call counts as success
            }

            // 2. Clear Storage
            localStorage.removeItem(STORAGE_KEY);

            // 3. SHOW RATING MODAL (If payment worked or was free)
            if (paymentSuccess && els.ratingModal) {
                els.ratingModal.style.display = "flex";
            } else {
                // Fallback if modal missing or payment failed
                alert(`Session Ended. Total Deduction: ₹${cost}`);
                window.location.href = "/client/consultations/";
            }
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
        // Only show "Free Intro" label if you consider the Fixed Fee to include the intro.
        // If you are charging the Fixed Fee immediately, you might want to remove the "Free Intro" text check
        // or change the text to "Base Charge Active".
        
        // Ensure billing starts tracking
        if (!state.billingActive) { 
            state.billingActive = true; 
        }
        
        const currentCost = calculateCost();
        const remaining = BALANCE - currentCost;

        // Warning if balance gets low
        if (remaining < (RATE * 2) && !state.warningShown && remaining > 0) {
            showToast("⚠️ Low Balance Warning");
            state.warningShown = true;
        }
        
        // Cut call if money runs out
        if (currentCost >= BALANCE) {
            call.leave();
            alert("Balance Exhausted.");
        }
    }

    function calculateCost() {
        const FIXED_FEE = 20;     // The fixed "Base Charge"
        const FREE_SECONDS = 120;  // 2 Minutes Trial

        // 1. Calculate billable time (Total time minus the 2 free minutes)
        // If seconds is 60, result is 0. If seconds is 130, result is 10.
        const billableDuration = Math.max(0, state.seconds - FREE_SECONDS);

        // 2. Calculate the variable cost based on the rate
        const variableCost = billableDuration * (RATE / 60);

        // 3. Total = Fixed Fee + Variable Cost
        return (FIXED_FEE + variableCost).toFixed(2);
    }

    function updateUI() {
        const m = String(Math.floor(state.seconds / 60)).padStart(2, "0");
        const s = String(state.seconds % 60).padStart(2, "0");
        els.timer.innerText = `${m}:${s}`;
        els.deduction.innerText = `₹${calculateCost()}`;
    }

    function showToast(msg) {
        if(els.toast) {
            els.toast.innerText = msg;
            els.toast.className = "show";
            setTimeout(() => els.toast.className = "", 3000);
        }
    }

    // --- RATING LOGIC (Global Scope) ---
    window.setRating = function(score) {
        document.getElementById("selected-rating").value = score;
        for (let i = 1; i <= 5; i++) {
            const star = document.getElementById(`star-${i}`);
            if (i <= score) {
                star.style.color = "#FFD700"; // Gold
                star.innerHTML = "★";
            } else {
                star.style.color = "#444";
                star.innerHTML = "★";
            }
        }
    };

    window.submitRating = async function() {
        const score = document.getElementById("selected-rating").value;
        const review = document.getElementById("review-text").value;
        
        if (score == 0) { alert("Please select a rating."); return; }

        try {
            await fetch("/api/rate_lawyer/", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
                body: JSON.stringify({ room_id: SESSION_ID, score: score, review: review })
            });
            window.location.href = "/client/consultations/";
        } catch (e) {
            console.error(e);
            window.location.href = "/client/consultations/";
        }
    };

    window.skipRating = function() {
        window.location.href = "/client/consultations/";
    };

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});