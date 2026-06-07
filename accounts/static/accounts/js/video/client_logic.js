document.addEventListener("DOMContentLoaded", function() {
    
    // 1. CONFIGURATION
    const STORAGE_KEY = `salah_session_${SESSION_ID}`;
    
    // Audio Recording Variables (Y-Splitter Method for Groq Whisper)
    let audioRecorder = null;
    let audioChunks = [];

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
    
    // Y-Splitter: Initialize silent audio recording when joining
    call.on("joined-meeting", async () => {
        console.log("========================================");
        console.log("🎙️ Y-SPLITTER DIAGNOSTIC START (CLIENT)");
        console.log("========================================");
        console.log("✅ Step 1: Joined meeting event triggered");
        
        try {
            // SOLUTION: Use browser's getUserMedia directly
            console.log("🎤 Step 2: Requesting microphone from browser...");
            
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true,
                video: false
            });
            
            console.log("✅ Step 3: Microphone stream obtained");
            const audioTrack = stream.getAudioTracks()[0];
            console.log("✅ Step 4: Audio track:", {
                label: audioTrack.label,
                enabled: audioTrack.enabled,
                readyState: audioTrack.readyState
            });
            
            // Check supported MIME types
            let mimeType = 'audio/webm';
            if (!MediaRecorder.isTypeSupported('audio/webm')) {
                console.warn("⚠️ audio/webm not supported, trying audio/mp4");
                mimeType = 'audio/mp4';
            }
            
            console.log("✅ Step 5: Creating MediaRecorder...");
            audioRecorder = new MediaRecorder(stream, { mimeType: mimeType });
                console.log("✅ Step 6: MediaRecorder initialized:", {
                    state: audioRecorder.state,
                    mimeType: audioRecorder.mimeType,
                    supported: MediaRecorder.isTypeSupported(mimeType)
                });
                
                // Clear previous chunks (prevent memory leak)
                audioChunks = [];
                console.log("✅ Step 7: Audio chunks array cleared");
                
                // Collect audio data chunks
                audioRecorder.ondataavailable = event => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                        console.log(`📦 Audio chunk received: ${event.data.size} bytes (Total chunks: ${audioChunks.length})`);
                    }
                };
                console.log("✅ Step 8: Data collection handler attached");
                
                // Handle recording stop (upload to backend)
                audioRecorder.onstop = async () => {
                    console.log("========================================");
                    console.log("🛑 RECORDING STOPPED - UPLOAD PROCESS");
                    console.log("========================================");
                    console.log(`📊 Total chunks collected: ${audioChunks.length}`);
                    
                    if (audioChunks.length > 0) {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        console.log(`📦 Audio blob created: ${(audioBlob.size / 1024).toFixed(2)} KB`);
                        
                        // Clear chunks immediately after creating blob to free memory
                        audioChunks = [];
                        console.log("🧹 Audio chunks cleared from memory");
                        
                        const formData = new FormData();
                        formData.append('audio_file', audioBlob, 'client_recording.webm');
                        formData.append('room_id', SESSION_ID);
                        console.log(`📤 Uploading to /api/process-audio/ with room_id: ${SESSION_ID}`);
                        
                        try {
                            const response = await fetch('/api/process-audio/', {
                                method: 'POST',
                                headers: {
                                    'X-CSRFToken': getCookie('csrftoken')
                                },
                                body: formData
                            });
                            
                            console.log(`📡 Server response status: ${response.status}`);
                            
                            if (response.ok) {
                                const result = await response.json().catch(() => ({}));
                                console.log("✅ CLIENT AUDIO UPLOADED SUCCESSFULLY");
                                console.log("📋 Server response:", result);
                            } else {
                                console.error("❌ UPLOAD FAILED - Server returned error");
                                console.error("Status:", response.status, response.statusText);
                                const errorText = await response.text().catch(() => "Unable to read error");
                                console.error("Error details:", errorText);
                            }
                        } catch (error) {
                            console.error("❌ UPLOAD ERROR - Network or fetch failed");
                            console.error("Error type:", error.name);
                            console.error("Error message:", error.message);
                            console.error("Full error:", error);
                        }
                    } else {
                        console.warn("⚠️ NO AUDIO CHUNKS - Nothing to upload");
                        console.warn("Possible causes:");
                        console.warn("1. Recording duration was too short");
                        console.warn("2. Microphone permission denied");
                        console.warn("3. Audio track became unavailable");
                    }
                };
                console.log("✅ Step 9: Stop handler attached");
                
                // Start recording silently with timeslice (collect data every 1 second)
                audioRecorder.start(1000); // 1000ms = 1 second chunks
                console.log("✅ Step 10: Recording started with 1-second intervals");
                console.log("========================================");
                console.log("🎙️ Y-SPLITTER ACTIVE (CLIENT)");
                console.log("Recording state:", audioRecorder.state);
                console.log("Microphone:", audioTrack.label);
                console.log("========================================");
                
                // Sync with Daily.co mute button
                setupMuteSync();
        } catch (error) {
            console.error("========================================");
            console.error("❌ Y-SPLITTER INITIALIZATION ERROR");
            console.error("========================================");
            console.error("Error name:", error.name);
            console.error("Error message:", error.message);
            
            if (error.name === 'NotAllowedError') {
                console.error("🚫 MICROPHONE PERMISSION DENIED");
                console.error("Solution: Click 'Allow' when browser asks for microphone access");
            } else if (error.name === 'NotFoundError') {
                console.error("🚫 NO MICROPHONE FOUND");
                console.error("Solution: Connect a microphone device");
            } else if (error.name === 'NotReadableError') {
                console.error("🚫 MICROPHONE IN USE");
                console.error("Solution: Close other apps using the microphone");
            }
            
            console.error("Stack trace:", error.stack);
            console.error("========================================");
        }
    });
    
    // Function to sync MediaRecorder with Daily.co mute button
    function setupMuteSync() {
        // Track mute state
        let lastMuteState = false;
        
        // Check mute state periodically (Daily.co doesn't have a direct mute event)
        const muteCheckInterval = setInterval(() => {
            if (!audioRecorder || audioRecorder.state === "inactive") {
                clearInterval(muteCheckInterval);
                return;
            }
            
            try {
                const currentMuteState = !call.localAudio();
                
                // Only act if state changed
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
        }, 500); // Check every 500ms
        
        console.log("✅ Mute button sync enabled");
    }
    
    //RELOAD HANDLER
    let isPageUnloading = false;
    window.addEventListener("beforeunload", () => {
        isPageUnloading = true;
        if(call) call.leave();
    });

    // --- LEFT MEETING (PAYMENT + MODAL TRIGGER) ---
    call.on("left-meeting", async () => {
        if (!isPageUnloading) {
            console.log("========================================");
            console.log("👋 LEFT MEETING - CLEANUP PROCESS");
            console.log("========================================");
            
            // Stop and upload audio recording FIRST
            if (audioRecorder) {
                console.log("📊 Recorder status:", {
                    exists: !!audioRecorder,
                    state: audioRecorder.state,
                    chunksCollected: audioChunks.length
                });
                
                if (audioRecorder.state !== "inactive") {
                    console.log("🛑 Stopping audio recorder...");
                    audioRecorder.stop();
                    console.log("⏳ Waiting 2 seconds for upload to complete...");
                    // Wait for upload to complete (onstop callback handles upload)
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    console.log("✅ Upload wait period completed");
                } else {
                    console.warn("⚠️ Recorder already inactive - no stop needed");
                }
            } else {
                console.warn("⚠️ No audio recorder found - recording may not have started");
            }
            console.log("========================================");
            
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

        if (remaining < (RATE * 2) && !state.warningShown && remaining > 0) {
            showToast("⚠️ Low Balance Warning");
            state.warningShown = true;
        }
        
        if (currentCost >= BALANCE) {
            call.leave();
            alert("Balance Exhausted.");
        }
    }

    function calculateCost() {
        const FIXED_FEE = 30;     
        const FREE_SECONDS = 20;  

        const billableDuration = Math.max(0, state.seconds - FREE_SECONDS);
        const variableCost = billableDuration * (RATE / 60);
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