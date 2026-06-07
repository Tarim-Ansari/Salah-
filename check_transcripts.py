from accounts.models import ConsultationRequest

consultations = ConsultationRequest.objects.all()
print(f"Total consultations: {consultations.count()}\n")

for c in consultations:
    has_transcript = "YES" if c.call_transcript else "NO"
    transcript_preview = c.call_transcript[:100] if c.call_transcript else "None"
    print(f"ID: {c.id}")
    print(f"Subject: {c.subject}")
    print(f"Status: {c.status}")
    print(f"Has Transcript: {has_transcript}")
    print(f"Preview: {transcript_preview}")
    print("-" * 60)

# Made with Bob
