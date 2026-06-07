# Solution: Displaying AI Questions in Video Call Sidebar

## Problem
You wanted to display the AI-generated recommended questions in the left sidebar of the client video call room, but were stuck because of the render/context issue.

## Root Issues Fixed

### 1. **Backend Issue in `views.py`** (Line 445)
**Problem**: Incorrect database query
```python
# WRONG - ConsultationRequest has no 'user' field
consultation_ques = ConsultationRequest.objects.get(user=request.user)
```

**Solution**: Use the already-fetched `consultation` object
```python
# CORRECT - Extract questions from the consultation we already have
questions = consultation.ai_client_checklist or []
```

### 2. **Context Not Passed to Template** (Line 492)
**Problem**: Questions were extracted but never added to the context dictionary
```python
# WRONG - questions variable created but not passed
questions = consultation_ques.ai_client_checklist
return render(request, template, context)  # context missing 'questions'
```

**Solution**: Add questions to the context for client template
```python
# CORRECT - Pass questions in context
context = {
    "room_url": daily_url,
    "session_id": room_id,
    "balance": request.user.wallet.balance, 
    "rate": 20,
    "questions": questions  # ← Added this
}
```

### 3. **Template Syntax Error** (Line 77 in client_room.html)
**Problem**: Incomplete Django template tag
```django
{% for question in %}  <!-- Missing variable name -->
```

**Solution**: Complete the loop with proper HTML structure
```django
{% if questions %}
    <ul style="list-style: none; padding: 0; margin-top: 10px;">
        {% for question in questions %}
            <li style="padding: 8px 0; border-bottom: 1px solid #222; color: #ccc; font-size: 0.85rem; line-height: 1.4;">
                <span style="color: var(--gold-accent); margin-right: 8px;">•</span>{{ question }}
            </li>
        {% endfor %}
    </ul>
{% else %}
    <p class="feedback-text" style="margin-top: 10px;">No questions available for this consultation.</p>
{% endif %}
```

## Complete Data Flow

### 1. **Case Brief Submission** (Pre-Call)
```
Client fills form → AI analyzes → Generates questions → Stored in DB
```
- Questions stored in `ConsultationRequest.ai_client_checklist` as JSON array
- Example: `["What are my legal rights?", "What is the timeline?", "What documents needed?"]`

### 2. **Video Call Join** (During Call)
```
Client clicks "Join Call" → join_room() view → Fetches consultation → Extracts questions → Passes to template
```

**Backend (`views.py` lines 442-493)**:
```python
@login_required
def join_room(request, room_id):
    # Get the consultation
    consultation = get_object_or_404(ConsultationRequest, room_id=room_id)
    
    # Extract questions (empty list if None)
    questions = consultation.ai_client_checklist or []
    
    # For CLIENT users, pass questions in context
    if request.user == consultation.client:
        context = {
            "room_url": daily_url,
            "session_id": room_id,
            "balance": request.user.wallet.balance,
            "rate": 20,
            "questions": questions  # ← Questions available in template
        }
        template = "accounts/video/client_room.html"
    
    return render(request, template, context)
```

### 3. **Template Rendering** (Display)
```
Template receives questions → Loops through list → Displays each question
```

**Frontend (`client_room.html` lines 75-91)**:
```html
<div class="feedback-box">
    <div class="info-label">AI Recommended Questions</div>
    {% if questions %}
        <ul>
            {% for question in questions %}
                <li>• {{ question }}</li>
            {% endfor %}
        </ul>
    {% else %}
        <p>No questions available</p>
    {% endif %}
</div>
```

## Visual Result

The sidebar will now display:

```
┌─────────────────────────┐
│ ⚖️ SALAH                │
│                         │
│ Status: Connected       │
│ Duration: 05:23         │
│                         │
│ Billing Feedback        │
│ Rate: ₹20/min          │
│ Total: ₹106.60         │
│                         │
│ AI Recommended Questions│
│ • What are my legal    │
│   rights in this case? │
│ • What is the expected │
│   timeline?            │
│ • What documents do I  │
│   need to prepare?     │
│                         │
│ [End Consultation]      │
└─────────────────────────┘
```

## Key Concepts Explained

### Why `consultation.ai_client_checklist or []`?
- If `ai_client_checklist` is `None` (no questions), use empty list `[]`
- Prevents template errors when trying to loop over `None`
- Safe fallback pattern

### Why Only Pass to Client Context?
- Questions are for the CLIENT to ask the LAWYER
- Lawyer doesn't need to see these questions in their view
- Keeps lawyer interface clean and focused

### Django Template Context
- Context is a Python dictionary passed to templates
- Keys become variables in the template
- `context = {"questions": [...]}` → `{{ questions }}` in template

## Testing the Fix

1. **Create a consultation** with AI analysis
2. **Accept the consultation** (generates room_id)
3. **Join the video call** as the client
4. **Check the sidebar** - questions should appear

## Files Modified

1. **`accounts/views.py`** (lines 442-493)
   - Fixed database query
   - Added questions extraction
   - Passed questions to client context

2. **`accounts/templates/accounts/video/client_room.html`** (lines 75-91)
   - Fixed incomplete template tag
   - Added proper loop structure
   - Added fallback message

## Status
✅ **COMPLETE** - Questions now display in video call sidebar