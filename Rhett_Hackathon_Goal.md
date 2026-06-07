# 🚀 Phase 1: Pre-Call (The AI Intake & Triage)

## Goal
Remove uncertainty before the call even starts.

---

## For the User

### AI Legal Assistant (Intake)
After filling the static form, the form is passed to the AI.  
The AI reads it and asks any clarification questions if required.

> This idea came from Eraser AI where the window is extended and the AI asks clarification questions before generating a flow chart.  
> We want to build something similar.

---

### Cost & Time Estimator (Tying into SALAH Wallet)
Since SALAH is Pay-Per-Minute, the AI analyzes the complexity of the case and says:

> “This is a complex NDA review. Estimated call time: 15–20 mins. Required Wallet Balance: ₹300.”

This directly supports Rhett's goal of **transparent pricing**.

---

### Recommended Questions
AI generates **3–5 specific questions** the user should ask the lawyer during the consultation.

---

## For the Lawyer

### AI Document Highlighting *(Future Scope / Optional)*
If the user uploads a contract, the AI highlights the critical or risky sections.

> This aligns well with the Track 1 prompt while fitting naturally into the Track 2 workflow.

---

---

# ⚡ Phase 2: During Call (The AI Co-Pilot)

## Goal
Make the live consultation **10x more efficient**.

---

## Under the Hood

### WebRTC + Speech-to-Text *(Future Scope)*
Generating a live transcript is one of the hardest but most impressive parts of the system.

---

### Live Translations (Hindi ↔ English)
If implemented successfully, this can become one of the strongest differentiators of the platform.

---

## For the User

### Dynamic Checklist
The “Recommended Questions” generated during the Pre-Call phase appear on screen.

#### Improvement Idea
Convert them into interactive checkboxes.

As the user asks each question, they can check it off so they do not forget anything during the consultation.

---

## For the Lawyer *(Optional / Future Scope)*

### Live Section Recommendations
As the user speaks, the transcript continuously feeds into the AI, which suggests relevant legal sections, compliance acts, or references on the lawyer’s sidebar.

---

### Real-Time Simplified Explanations for Users
When the lawyer mentions legal sections or complex law-related terminology that the user may not understand, the AI generates a short and simple explanation on the side panel for the user.

---

---

# 🏁 Phase 3: Post-Call (Execution & Tracking)

## Goal
Do not leave the client hanging after the consultation. Deliver actionable outcomes.

---

## For the User

### Execution Plan / Summary
The AI reads the transcript and instantly generates:

- A concise summary of the consultation
- Key decisions discussed
- Exact next steps for the user

---

### Case Timeline
A visual tracker appears on the user dashboard.

Example:

- ✅ Step 1: Consultation
- ⏳ Step 2: Lawyer Drafts Notice
- ⏳ Step 3: File with Court

---

## For the Lawyer — *The “Document Forge”*

### AI Draft Assistant
Instead of supporting 50+ templates, focus on only **1–2 key legal drafts** for the hackathon.

Examples:
- Legal Notice
- NDA

---

### The Magic
The AI uses the consultation transcript to auto-fill the template.

The lawyer only needs to:
1. Review
2. Make minor edits
3. Click **“Send to Client”**

This significantly reduces repetitive drafting work.

---

# ✨ Extra Feature

If there are certain documents that users can legally draft on their own without lawyer supervision, they can use our platform to generate those drafts directly using AI assistance.

> Only simple self-service drafts that do not require legal supervision would be supported in this workflow.