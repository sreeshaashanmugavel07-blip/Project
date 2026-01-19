# Quick Start Guide - Community Issue Reporting Assistant

## Prerequisites Setup

1. **Supabase**
   - Create account at https://supabase.com
   - Create new project
   - Run SQL from `backend/supabase_schema.sql` in SQL Editor
   - Copy Project URL and Anon Key

2. **OpenAI**
   - Get API key from https://platform.openai.com/api-keys

3. **Webhook (Optional)**
   - Use https://webhook.site for testing
   - Or set up your own endpoint

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your keys
python main.py
```

Backend runs on http://localhost:8000

### Frontend

```bash
cd frontend
npm install
# Create .env file with: VITE_API_URL=http://localhost:8000
npm run dev
```

Frontend runs on http://localhost:5173

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
WEBHOOK_URL=https://webhook.site/xxx (optional)
ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Testing the Flow

1. Open frontend at http://localhost:5173
2. You'll see greeting: "Hello! I am the Community Helpdesk Assistant..."
3. Enter your name (e.g., "John Doe")
4. Select issue type (e.g., "Garbage")
5. Provide location (e.g., "123 Main Street")
6. Describe the issue
7. Provide phone number
8. Confirm details (Yes/No)
9. See success message

## Deployment

See main README.md for detailed deployment instructions to Render (backend) and Vercel (frontend).
