# 🏠 RealEstate AI EdTech — FastAPI + Groq

Zero-cost AI-powered real estate advisory backend that captures leads automatically.

---

## Stack
| Layer | Tool | Cost |
|-------|------|------|
| AI Model | Groq (Mixtral-8x7b) | FREE tier |
| Backend | FastAPI + Python | Free |
| Hosting | Render.com (free web service) | FREE |
| Database | In-memory (upgrade to Supabase free tier later) | FREE |

---

## Local Setup

```bash
# 1. Clone / copy files
cd realestate_ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Run locally
uvicorn main:app --reload
# → API running at http://localhost:8000
# → Swagger docs at http://localhost:8000/docs
```

---

## Get Your FREE Groq API Key

1. Go to https://console.groq.com
2. Sign up (free, no credit card)
3. Create API Key → copy it
4. Paste into your `.env` file

---

## Deploy to Render.com (FREE, EOD)

1. Push code to GitHub (new repo)
2. Go to https://render.com → New → Web Service
3. Connect your GitHub repo
4. Set environment variables:
   - `GROQ_API_KEY` = your key
   - `ADMIN_SECRET` = any secret password
5. Click **Deploy** → Done in ~3 minutes
6. Your API is live at: `https://your-app.onrender.com`

---

## API Endpoints

### POST /chat
Send a message and get AI response.
```json
{
  "session_id": "user_abc123",
  "message": "I want to invest in property in Bangalore",
  "history": []
}
```
Response:
```json
{
  "reply": "Great choice! Bangalore's real estate...",
  "session_id": "user_abc123",
  "lead_detected": false
}
```

### POST /leads/capture
Explicitly save a lead (call after form submission).
```json
{
  "session_id": "user_abc123",
  "name": "Ravi Kumar",
  "email": "ravi@email.com",
  "phone": "9876543210",
  "interest": "Investment"
}
```

### GET /leads?secret=yourpassword
View all captured leads (admin only).

### GET /health
Health check.

---

## Adding Your Prompt

In `main.py`, replace the `SYSTEM_PROMPT` variable content with your custom prompt.

---

## Next Steps (when you have budget)
- Replace in-memory leads with **Supabase** (free PostgreSQL)
- Add WhatsApp lead notification via **Twilio free tier**
- Add a frontend chat widget (React/HTML) connected to this API
