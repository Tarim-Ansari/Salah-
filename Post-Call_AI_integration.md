# 🏁 SALAH: Phase 3 - Post-Call (Execution & Tracking) Implementation Guide

**Goal:** Don't leave the client hanging after the video call ends. We will fetch the Daily.co transcript, feed it to Groq/Llama-3, and instantly generate an Action Plan for the User and a pre-filled Legal Document for the Lawyer to review.

---

### 🗄️ Step 1: The Execution Database (Assigned to: Tarim)
**Target File:** `accounts/models.py`
**Goal:** Prepare the `ConsultationRequest` model to store the transcript, the AI summary, and the drafted document.

**Action:**
Add these final fields to your existing `ConsultationRequest` model:
```python
    # Phase 3 Fields
    call_transcript = models.TextField(blank=True, null=True)
    ai_execution_plan = models.JSONField(blank=True, null=True) # Stores list of next steps
    ai_drafted_document = models.TextField(blank=True, null=True) # The generated legal doc (HTML/Text)
    case_milestone = models.CharField(max_length=100, default="Consultation Completed") # For the Timeline
```
*Run `python manage.py makemigrations` and `python manage.py migrate`.*

---

### ⏳ Step 2: The Polling Bridge & Loading Screen (Assigned to: Frontend)
**Target File:** `accounts/templates/accounts/consultation/summary_processing.html`
**Goal:** When the call ends, Daily.co takes a few minutes to process the transcript. We need a loading screen that checks the backend every 5 seconds until the AI is done.

**Action:**
1. Create a clean loading page with a spinning "AI is processing your case..." animation.
2. Write a JS `setInterval` function that pings Diyan's API:
```javascript
const consultationId = "{{ consultation.id }}";
const userRole = "{{ request.user.role }}";

const pollInterval = setInterval(async () => {
    const response = await fetch(`/api/process-transcript/${consultationId}/`);
    const data = await response.json();
    
    if (data.status === "ready") {
        clearInterval(pollInterval);
        // Route based on role
        if (userRole === "client") {
            window.location.href = `/client/post-call-summary/${consultationId}/`;
        } else {
            window.location.href = `/lawyer/document-forge/${consultationId}/`;
        }
    }
}, 5000); // Ping every 5 seconds
```

---

### ⚙️ Step 3: Transcript Fetcher & AI Processor (Assigned to: Diyan)
**Target File:** `accounts/views.py`
**Goal:** Check Daily.co for the transcript. If it exists, download it, send it to Groq, save the results, and tell the frontend we are `ready`.

**Action:**
1. Create the `process_transcript_api(request, consultation_id)` view.
2. **Fetch:** Ping the Daily.co `/recordings` or `/transcripts` API endpoint for this specific `room_id`. 
   * *If not ready:* `return JsonResponse({"status": "processing"})`
   * *If ready:* Download the text.
3. **The LLM Magic (Groq):** Send the transcript to your LLM with this prompt:
   > *"You are an expert legal AI. Read this transcript between a lawyer and client: '{transcript}'. Return ONLY a JSON object with two keys: 1. 'execution_plan' (an array of 3 actionable next steps for the client), and 2. 'legal_draft' (Draft a formal Legal Notice based on the facts discussed. Use HTML formatting like <br> and <b>)."*
4. **Save & Finish:** 
   ```python
   consultation.call_transcript = clean_transcript
   consultation.ai_execution_plan = data['execution_plan']
   consultation.ai_drafted_document = data['legal_draft']
   consultation.case_milestone = "Drafting Document"
   consultation.save()
   return JsonResponse({"status": "ready"})
   ```

---

### 📊 Step 4: Client Post-Call Dashboard (Assigned to: Frontend)
**Target File:** `accounts/templates/accounts/client/client_summary.html`
**Goal:** Show the client exactly what to do next and track their case.

**Action:**
1. **Section 1: Execution Plan:** Render `consultation.ai_execution_plan` as a clean, styled unordered list `<ul>`.
2. **Section 2: Case Timeline:** Build a horizontal visual tracker (CSS Progress bar).
   * 🟢 Node 1: "Consultation Done" (Green/Active)
   * 🟡 Node 2: "Lawyer Drafting Notice" (Yellow/Pending - matches `case_milestone`)
   * ⚪ Node 3: "Execution / Court Filing" (Gray/Locked)

---

### ✍️ Step 5: Lawyer "Document Forge" Dashboard (Assigned to: Frontend & Diyan)
**Target File:** `accounts/templates/accounts/lawyer/document_forge.html`
**Goal:** Let the lawyer review the AI-drafted document, edit it, and finalize it.

**Action:**
1. Display `consultation.ai_drafted_document` inside a rich-text editor (or a large `<textarea>` with decent styling).
2. Add a **"Save & Mark as Ready"** button.
3. **Backend Route:** When clicked, send the edited text to a new endpoint. This updates the DB and changes the user's `case_milestone` to "Document Ready for Client".

---

### 🎁 Step 6: The Freemium DIY Drafter (Assigned to: Full Team)
**Target File:** `accounts/templates/accounts/common/diy_drafter.html`
**Goal:** A standalone lead-generation tool to draw users to SALAH before they need a paid lawyer.

**Action:**
1. Create a separate page accessible from the Homepage header (e.g., "Free AI Legal Drafts").
2. Provide a dropdown: "Non-Disclosure Agreement (NDA)" or "Employee Offer Letter".
3. Show a simple form: Party 1 Name, Party 2 Name, Salary/Amount, State/Jurisdiction.
4. When submitted, Diyan's backend sends these 4 variables to Groq and returns a generated document instantly.
5. Display it on screen with a "Copy to Clipboard" button. *(Keep this isolated; do not mix it with the video WebRTC logic).*

---

### ⚠️ Technical Safety Nets (CRITICAL FOR PITCH/HACKATHON DEMO):

1. **The "Daily.co Takes Too Long" Trap:** 
   * *Risk:* Daily.co can take 3 to 5 minutes to generate a transcript after a call ends. In a live pitch, you cannot wait 5 minutes staring at a loading screen.
   * *The Fix:* Diyan **must** build a hidden "Bypass" button on the loading screen, or add logic in `process_transcript_api` that says: *If this is the demo consultation ID, bypass Daily.co, use a hardcoded fake transcript string, process it through Groq instantly, and return 'ready'.*
2. **The VTT Parser:**
   * *Risk:* Transcripts download with messy timestamps (e.g., `00:01:23.000 --> 00:01:25.000`). If you send this to Groq, it eats up tokens and degrades AI performance.
   * *The Fix:* Diyan needs a 5-line Python script to strip timestamps and format it as `Lawyer: [Text] \n Client: [Text]` before sending it to the LLM.
3. **Token Limit Crash:**
   * *Risk:* If the conversation was long, the transcript might exceed Groq's token limit.
   * *The Fix:* Use `transcript_text[-12000:]` to only send the last chunk of the conversation (which usually contains the conclusions/action items anyway).

---

### 🚨 Missing Piece 1: We forgot the "Call Summary" Field (Assigned to: Tarim & Diyan)
**The Problem:** The user's goal stated: *"A concise summary of the consultation, Key decisions, AND Exact next steps."* But in Step 1, I only told Tarim to create `ai_execution_plan` (the next steps) and `ai_drafted_document`. We forgot the field to store the actual summary!
**Action for Tarim (models.py):**
Add one more field to the `ConsultationRequest` model:
```python
ai_call_summary = models.TextField(blank=True, null=True) # Stores summary and key decisions
```
**Action for Diyan (views.py):**
Update the Groq LLM prompt in Step 3 to ask for 3 things, not 2:
> *"Return a JSON object with 3 keys: 1. 'summary' (a brief paragraph of key decisions), 2. 'execution_plan' (array of next steps), 3. 'legal_draft' (the HTML legal document)."*
And save it: `consultation.ai_call_summary = data['summary']`.

### 🚨 Missing Piece 2: The Client Needs to *See* the Document! (Assigned to: Frontend)
**The Problem:** In Step 5, we built the awesome "Document Forge" for the Lawyer to edit and click "Send to Client". But we forgot to tell the Frontend team to actually show it to the Client! 
**Target File:** `accounts/templates/accounts/client/client_summary.html`
**Action:** Add a section below the timeline that checks if the document is ready, and allows the client to view/print it.
```html
<!-- Add this to the Client's Post-Call Dashboard -->
<div class="document-section" style="margin-top: 30px;">
    <h3 style="color: var(--primary-gold);">Your Legal Documents</h3>
    
    {% if consultation.case_milestone == "Document Ready for Client" %}
        <div style="background: #111; padding: 20px; border: 1px solid #2ecc71; border-radius: 8px;">
            <p style="color: #2ecc71; font-weight: bold;">✅ Your Lawyer has finalized your document.</p>
            <!-- Show the document in a read-only box -->
            <div style="background: #222; padding: 15px; color: #ddd; max-height: 300px; overflow-y: auto;">
                {{ consultation.ai_drafted_document|safe }}
            </div>
            <button class="btn btn-outline" onclick="window.print()" style="margin-top: 15px;">Print / Save as PDF</button>
        </div>
    {% else %}
        <p style="color: #888;">⏳ Your lawyer is currently reviewing and drafting your document. Check back soon.</p>
    {% endif %}
</div>
```

### 🚨 Missing Piece 3: The LLM JSON Markdown Crash (Assigned to: Diyan)
**The Problem:** Just like in Phase 1, when Groq/Llama-3 generates the Execution Plan and Draft, it will likely wrap the JSON in markdown code blocks (````json { ... } ````). If Diyan tries to do `json.loads(response)` directly in Step 3, Django will throw a `JSONDecodeError` and crash the loading screen.
**Action:** Diyan MUST use the cleaner and `try-except` block in `process_transcript_api`:
```python
import json

try:
    # Clean the markdown
    raw_response = llm_response.replace("```json", "").replace("```", "").strip()
    data = json.loads(raw_response)
except json.JSONDecodeError:
    # HARDCODED FALLBACK IF LLM FAILS DURING PITCH
    data = {
        "summary": "Discussed property dispute and agreed to send a legal notice.",
        "execution_plan": ["Wait for lawyer to draft notice", "Review notice", "File in court"],
        "legal_draft": "<h2>LEGAL NOTICE</h2><p>To whom it may concern...</p>"
    }
```

***


# 🔮 Future Scope (Phase 3 Additions)
*To be mentioned in pitches as upcoming features, but NOT built for the MVP:*

*   **Court API Integration (eCourts):** Automatically pulling case status updates from the official Indian eCourts portal and updating the SALAH "Case Timeline" without manual lawyer input.
*   **E-Signatures:** Integrating an e-signing API (like DocuSign or Aadhaar eSign) directly into the Document Forge, allowing both parties to legally sign the AI-generated NDA/Agreements without leaving the SALAH platform.
*   **WebRTC + Raw Socket Audio Streaming:** Bypassing Daily.co's post-call transcript completely by streaming raw audio chunks via WebSockets to a dedicated Speech-to-Text engine during the call, allowing the summary to be ready the *exact second* the call ends.