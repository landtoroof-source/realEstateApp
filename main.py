from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
from groq import Groq
from datetime import datetime
import json
from dotenv import load_dotenv

app = FastAPI(title="RealEstate AI EdTech", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading environment variables...")
load_dotenv()  # Load from .env file
print("Environment variables loaded:")
print(f"GROQ_API_KEY: {os.environ.get('GROQ_API_KEY')}")
print(f"ADMIN_SECRET: {os.environ.get('ADMIN_SECRET')}")
# ── Groq client ──────────────────────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# ── In-memory lead store (replace with DB later) ──────────────────────────────
leads_db: list[dict] = []

# ── System prompt (paste your own below) ─────────────────────────────────────
SYSTEM_PROMPT = """
You are an expert AI real estate advisor and educator working for a premium EdTech platform.

Your goals:
1. Educate users about real estate — buying, renting, investing, market trends, and property valuation.
2. Give personalized, actionable suggestions based on the user's budget, location, and goals.
3. Build trust by explaining concepts clearly (EMI, ROI, RERA, carpet area, etc.).
4. Naturally guide the conversation toward capturing the user's name, email, and phone number
   so our team can follow up with exclusive deals and free consultations.

Lead capture rules:
- After 2–3 helpful exchanges, politely ask: "Would you like a FREE consultation call with our
  real estate experts? Just share your name and contact details."
- If user shares contact info, confirm you've noted it and say the team will reach out within 24hrs.
- Never be pushy. Be warm, knowledgeable, and helpful first.

Always respond in the same language the user writes in (English or local language mix is fine).
Keep responses concise — 3–5 sentences max unless explaining a complex topic.
"""

# ── Schemas ───────────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    session_id: str
    message: str
    history: Optional[list[dict]] = []

class Lead(BaseModel):
    session_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    interest: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    lead_detected: bool = False

# ── Simple keyword-based lead detection ───────────────────────────────────────
def detect_lead_info(text: str) -> dict:
    import re
    lead = {}
    email = re.findall(r'[\w.+-]+@[\w-]+\.\w+', text)
    phone = re.findall(r'[\+]?[\d\s\-]{10,13}', text)
    if email:
        lead["email"] = email[0]
    if phone:
        lead["phone"] = phone[0].strip()
    return lead

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "service": "RealEstate AI EdTech API"}

@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatMessage):
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Include conversation history
        for h in payload.history[-10:]:  # keep last 10 turns
            messages.append(h)

        messages.append({"role": "user", "content": payload.message})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=512,
        )

        reply = response.choices[0].message.content

        # Check if user shared contact info
        lead_info = detect_lead_info(payload.message)
        lead_detected = bool(lead_info)

        if lead_detected:
            leads_db.append({
                "session_id": payload.session_id,
                "timestamp": datetime.utcnow().isoformat(),
                **lead_info
            })

        return ChatResponse(
            reply=reply,
            session_id=payload.session_id,
            lead_detected=lead_detected
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/leads/capture")
def capture_lead(lead: Lead):
    """Explicit lead capture endpoint (call when user fills a form)."""
    record = {
        **lead.dict(),
        "timestamp": datetime.utcnow().isoformat(),
        "source": "explicit_form"
    }
    leads_db.append(record)
    return {"status": "captured", "lead_id": len(leads_db)}


@app.get("/leads")
def get_leads(secret: str = ""):
    """Simple admin endpoint — protect with secret key in prod."""
    if secret != os.environ.get("ADMIN_SECRET", "changeme"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"total": len(leads_db), "leads": leads_db}


@app.get("/health")
def health():
    return {"status": "healthy", "model": MODEL, "timestamp": datetime.utcnow().isoformat()}
