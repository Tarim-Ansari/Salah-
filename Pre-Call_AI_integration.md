# ⚖️ SALAH: Phase 1 - AI Intake & Triage Implementation Guide

**Goal:** Integrate an "Eraser-style" AI assistant into the existing Case Brief submission process. It will clarify the user's legal issue, estimate the time/cost, provide a consultation checklist, and verify their SALAH Wallet balance before routing the request to the lawyer.

---

### 🗄️ Step 1: Database Updates (Assigned to: Diyan)  ✅ Task completed
**Target File:** `accounts/models.py`
**Goal:** Update the existing `ConsultationRequest` model to store the new AI-generated insights.

**Action:**
Add these new fields to the `ConsultationRequest` model:
```python
# accounts/models.py
from django.db.models import JSONField # Make sure this is imported if not already

class ConsultationRequest(models.Model):
    # ... (Keep existing fields: client, lawyer, category, subject, description, status, etc.) ...
    
    # NEW AI FIELDS
    ai_refined_description = models.TextField(blank=True, null=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) 
    estimated_duration = models.IntegerField(blank=True, null=True) # In minutes
    ai_client_checklist = models.JSONField(blank=True, null=True) # Stores list of questions
```
*Run `python manage.py makemigrations` and `python manage.py migrate` after saving.*

---

### 🎨 Step 2: The "Eraser-Style" Intake UI (Assigned to: Frontend Team)  ✅ Task completed (Changes in HTML Required)
**Target File:** `accounts/templates/accounts/client/case_brief.html`
**Goal:** Modify the existing case brief form to include hidden div containers for the AI Chat and the Final Dashboard. Keep it aligned with the dark/gold theme.

**Action:**
1. Keep the standard form (Category, Subject, Description) but change the Submit button to type `button` and give it an ID: `<button type="button" id="start-ai-btn">Analyze My Case</button>`
2. Add the hidden AI Chat Window below the form:
```html
<!-- Hidden AI Chat Window -->
<div id="ai-chat-window" style="display: none; border-left: 3px solid var(--primary-gold); padding: 15px; margin-top: 20px; background: #111;">
    <p style="color: var(--primary-gold); font-weight: bold;">SALAH AI Assistant:</p>
    <p id="ai-question" style="color: #fff;">Thinking...</p>
    <input type="text" id="user-reply" placeholder="Type your answer here..." style="width:100%; padding: 10px; background: #222; border: 1px solid #444; color: #fff; margin-top: 10px;">
    <button type="button" id="send-reply-btn" class="submit-btn" style="margin-top: 10px;">Reply</button>
</div>
```
3. Add the hidden Triage Dashboard:
```html
<!-- Hidden Triage Dashboard -->
<div id="triage-dashboard" style="display: none; margin-top: 30px;">
    <h3 style="color: var(--primary-gold);">Consultation Plan</h3>
    <p><strong>Estimated Time:</strong> <span id="est-time"></span> mins</p>
    <p><strong>Estimated Cost:</strong> ₹<span id="est-cost"></span></p>
    
    <h4>Questions to ask the Lawyer:</h4>
    <ul id="checklist-container" style="color: #ccc; padding-left: 20px;"></ul>
    
    <div id="wallet-action-container" style="margin-top: 20px;">
        <!-- Buttons injected via JS based on wallet balance -->
    </div>
</div>
```

---

### ⚙️ Step 3: Evaluation API (Assigned to: Diyan)  ✅ Task completed
**Target File:** `accounts/views.py`
**Goal:** The endpoint that talks to Groq/Llama-3 to check if the description needs more context.

**Action:**
1. Create a new view `evaluate_intake(request)`.
2. Extract the `description` and `chat_history` from the JSON payload.
3. Prompt the LLM: 
   > *"You are a legal intake paralegal. Review this client's issue: '{description}'. Chat history: '{chat_history}'. If it lacks crucial legal context, ask EXACTLY ONE simple clarifying question. If it has enough context to route to a lawyer, output ONLY the exact word 'COMPLETE'."*
4. Return JSON: `{"status": "ask_question", "message": "<Question>"}` or `{"status": "complete"}`.
5. Map this in `urls.py` as `path('api/evaluate-intake/', views.evaluate_intake, name='evaluate_intake')`.

---

### 🧠 Step 4: The Chat & Wallet Logic (Assigned to: Frontend/Yogesh for QA)
**Target File:** `<script>` tag inside `case_brief.html`
**Goal:** Connect the UI to Diyan's API securely using SALAH's existing CSRF token system.

**Action:**
1. Read the user's wallet balance natively using Django: `const USER_BALANCE = parseFloat("{{ user.wallet.balance|default:'0' }}");`
2. Write the `fetch` logic using the exact CSRF method already used in SALAH's video rooms:
```javascript
// Function to talk to AI
async function sendToAI(description, chatHistory) {
    const response = await fetch("/api/evaluate-intake/", {
        method: "POST",
        headers: { 
            "Content-Type": "application/json", 
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value // NO EXEMPT NEEDED!
        },
        body: JSON.stringify({ description: description, chat_history: chatHistory })
    });
    // Handle ask_question (unhide chat div) or complete (trigger finalizer API)
}
```

---

### 🛡️ Step 5: Finalizer API & Database Save (Assigned to: Diyan) ✅ Task completed
**Target File:** `accounts/views.py`
**Goal:** Generate the checklist, estimate cost, and actually save the `ConsultationRequest` object to the database.

**Action:**
1. Create `finalize_intake(request)`.
2. Prompt LLM: *"Based on '{full_context}', output ONLY a JSON object: {"estimated_minutes": [int], "client_questions": ["Q1", "Q2", "Q3"]}."*
3. **CRITICAL: The Hallucination Safety Net.** You *must* wrap the JSON parsing in a `try-except` block to prevent demo crashes:
```python
import json

try:
    # Clean markdown formatting if LLM includes it
    raw_response = llm_response.replace("```json", "").replace("```", "").strip()
    data = json.loads(raw_response)
except json.JSONDecodeError:
    # FALLBACK DUMMY DATA FOR LIVE DEMO SAFETY
    data = {"estimated_minutes": 15, "client_questions": ["What are my legal rights?", "What is the next step?"]}
```
4. Calculate Cost: `est_cost = data['estimated_minutes'] * 20` (Using your ₹20/min rate).
5. **Create the DB Record:** 
   ```python
   ConsultationRequest.objects.create(
       client=request.user,
       lawyer_id=request.POST.get('lawyer_id'), # Passed from frontend
       category_id=request.POST.get('category_id'),
       subject=request.POST.get('subject'),
       description=full_context,
       ai_refined_description=full_context,
       estimated_cost=est_cost,
       estimated_duration=data['estimated_minutes'],
       ai_client_checklist=data['client_questions'],
       status="pending"
   )
   ```
6. Return `{"status": "success", "estimated_minutes": ..., "estimated_cost": ...}`.

---

### 💳 Step 6: The Triage Dashboard & Wallet Verification (Assigned to: Frontend)
**Target File:** `case_brief.html` (JS portion)
**Goal:** Render the final data and check if the user has enough money in their SALAH wallet to afford the estimated time.

**Action:**
Once `/api/finalize-intake/` returns success:
1. Hide the original form and chat window.
2. Unhide `triage-dashboard`.
3. Populate `est-time`, `est-cost`, and generate `<li>` tags for the checklist.
4. **The Wallet Bridge Logic:**
```javascript
const estCost = response.estimated_cost;
const walletActionContainer = document.getElementById('wallet-action-container');

if (USER_BALANCE >= estCost) {
    walletActionContainer.innerHTML = `<button class="btn btn-accept" onclick="window.location.href='/client/consultations/'">Sufficient Balance: Send Request to Lawyer</button>`;
} else {
    walletActionContainer.innerHTML = `
        <p style="color: #e74c3c;">Low Balance. You need ₹${estCost} but only have ₹${USER_BALANCE}.</p>
        <button class="btn btn-reject" onclick="window.location.href='/wallet/'">Top Up Wallet First</button>
    `;
}
```

***

### 🚨 Missing Piece 1: Showing the AI Insights to the Lawyer (Assigned to: Frontend)
**The Problem:** We saved `ai_refined_description` and `estimated_duration` to the database in Step 5, but we forgot to update the Lawyer's UI to actually display it! What is the point of the AI if the lawyer doesn't see the results?
**Target File:** `accounts/templates/accounts/lawyer/request_detail.html`
**Action:** Add this block right below the original description so the lawyer can see the AI's summary and the estimated time:
```html
<!-- AI Insights Section -->
{% if req.ai_refined_description %}
<div class="brief-section" style="border-left: 3px solid #2ecc71; background: #111; margin-top: 20px;">
    <label class="brief-label" style="color: #2ecc71;">🤖 AI Refined Case Summary</label>
    <div class="brief-content">{{ req.ai_refined_description }}</div>
    <div style="margin-top: 15px; color: #aaa; font-size: 0.85rem;">
        <strong>AI Estimated Duration:</strong> {{ req.estimated_duration }} mins
    </div>
</div>
{% endif %}
```

### 🚨 Missing Piece 2: Passing the Correct IDs in JavaScript (Assigned to: Frontend/Diyan)
**The Problem:** Because we are stopping the normal HTML `<form>` from submitting and using JavaScript `fetch()` instead, Django won't know *which* lawyer or category the client selected unless we explicitly send it in the JavaScript.
**Target File:** `case_brief.html` (JS portion)
**Action:** Yash must grab the `lawyer_id` and `category_id` from the page and send them in the `finalize_intake` fetch call.
```javascript
// Add these to the frontend JS payload in Step 5
const lawyerId = "{{ lawyer.id }}"; // Pulled from Django template
const categoryId = document.querySelector('select[name="category"]').value;
const subject = document.querySelector('input[name="subject"]').value;

// Send them to Diyan's API so he can save the ConsultationRequest properly
```

# 🔮 Future Scope (Phase 2 & Beyond)

*To be mentioned at the end of pitch decks as upcoming features:*

*   **AI Document Highlighting for Lawyers:** When a client uploads a legal contract (PDF/Image) during intake, an OCR-powered AI agent will scan the document and highlight risky clauses or missing signatures. This highlighted version will be visible exclusively on the Lawyer's Dashboard, saving them 10-15 minutes of prep time before the video call begins.
*   **Post-Call Transcription & Summary:** AI automatically transcribes the WebRTC video call audio and saves a "Key Action Items" summary to both the client's and lawyer's dashboards.


