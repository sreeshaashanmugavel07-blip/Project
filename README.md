# AI-Based Community Issue Reporting Assistant

A full-stack AI-powered community helpdesk application with a chat-based interface for residents to report community issues (Garbage, Water, Road, Streetlight, Drainage, etc.).

## Tech Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Python + FastAPI
- **Database**: Supabase
- **AI**: OpenAI GPT-4o-mini (via LangChain)
- **Conversation Flow**: Custom state machine
- **Hosting**: Frontend on Vercel, Backend on Render

## Features

- 💬 Chat-based interface for issue reporting
- 🤖 AI-powered digital receptionist conversation flow
- 📊 Complaints stored in Supabase
- 🔔 Webhook integration for forwarding complaints
- 🎨 Clean and modern UI with chat bubbles
- 📱 Responsive design
- 🔄 Multi-step conversation flow (Name → Issue Type → Location → Description → Phone → Confirmation)

## Conversation Flow

1. **Greet** - System greeting
2. **Ask Name** - Collect user's name
3. **Ask Issue Type** - Garbage, Water, Road, Streetlight, Drainage, Others
4. **Ask Location** - Address or location of issue
5. **Ask Description** - Detailed description
6. **Ask Phone** - Contact number for follow-up
7. **Confirm** - Show summary and confirm details
8. **Save** - Store in Supabase and trigger webhook
9. **Success** - Show confirmation message

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── main.py          # Main API application with conversation flow
│   ├── requirements.txt
│   ├── Procfile         # For Render deployment
│   ├── env.example      # Environment variables template
│   └── supabase_schema.sql
├── frontend/            # React frontend
│   ├── src/
│   │   ├── App.jsx      # Main chat component
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- Supabase account
- OpenAI API key
- Render account (for backend)
- Vercel account (for frontend)

### 1. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run the SQL from `backend/supabase_schema.sql`:
   ```sql
   CREATE TABLE IF NOT EXISTS complaints (
       id BIGSERIAL PRIMARY KEY,
       name TEXT NOT NULL,
       issue_type TEXT NOT NULL,
       location TEXT NOT NULL,
       description TEXT NOT NULL,
       phone TEXT NOT NULL,
       timestamp TIMESTAMPTZ DEFAULT NOW()
   );
   ```
3. Go to Project Settings > API
4. Copy your:
   - Project URL (SUPABASE_URL)
   - Anon/Public Key (SUPABASE_KEY)

### 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```bash
   cp env.example .env
   ```

5. Edit `.env` and add your credentials:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   WEBHOOK_URL=your_webhook_url_optional
   ALLOWED_ORIGINS=http://localhost:5173
   ```
   
   **Note**: `WEBHOOK_URL` is optional. If not provided, webhook functionality will be skipped.

6. Run the backend locally:
   ```bash
   python main.py
   ```
   
   Or using uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

### 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your backend URL:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

5. Run the development server:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## Deployment

### Backend Deployment on Render

1. **Create a Render Account**
   - Go to [render.com](https://render.com) and sign up

2. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or use Render's manual deploy)

3. **Configure the Service**
   - **Name**: `community-issue-assistant-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   - Go to Environment section
   - Add the following:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `SUPABASE_URL`: Your Supabase project URL
     - `SUPABASE_KEY`: Your Supabase anon key
     - `WEBHOOK_URL`: (Optional) Your webhook URL to receive complaints
     - `ALLOWED_ORIGINS`: Your Vercel frontend URL (e.g., `https://your-project.vercel.app`) - add this after deploying frontend

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Copy your service URL (e.g., `https://community-issue-assistant-api.onrender.com`)

### Frontend Deployment on Vercel

1. **Create a Vercel Account**
   - Go to [vercel.com](https://vercel.com) and sign up

2. **Import Your Project**
   - Click "Add New..." → "Project"
   - Import your GitHub repository (or upload the frontend folder)

3. **Configure the Project**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend` (if deploying from monorepo)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. **Add Environment Variables**
   - Go to Settings → Environment Variables
   - Add:
     - `VITE_API_URL`: Your Render backend URL (e.g., `https://community-issue-assistant-api.onrender.com`)

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Your app will be live at `https://your-project.vercel.app`

### Post-Deployment Steps

1. **Update Backend CORS**
   - Go to Render dashboard → Your backend service → Environment
   - Add/Update `ALLOWED_ORIGINS` environment variable with your Vercel frontend URL:
     ```
     https://your-project.vercel.app
     ```
   - If you have multiple origins, separate with commas
   - Redeploy the service (or it will auto-redeploy)

2. **Test the Application**
   - Visit your Vercel URL
   - Start a conversation
   - Complete the full flow and verify complaint is saved

## API Endpoints

### POST /chat

Send a message to the AI assistant and continue the conversation flow.

**Request Body:**
```json
{
  "message": "John Doe",
  "session_id": "session_1234567890"
}
```

**Response:**
```json
{
  "reply": "Thank you, John Doe. What type of issue are you reporting?",
  "session_id": "session_1234567890",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Note**: `session_id` is optional on first request. The backend will generate one and return it for subsequent requests.

### GET /health

Check backend health and configuration status.

**Response:**
```json
{
  "status": "healthy",
  "supabase_connected": true,
  "openai_configured": true,
  "webhook_configured": true
}
```

## Environment Variables

### Backend (.env)

- `OPENAI_API_KEY`: Your OpenAI API key (Required)
- `SUPABASE_URL`: Your Supabase project URL (Required)
- `SUPABASE_KEY`: Your Supabase anon/public key (Required)
- `WEBHOOK_URL`: (Optional) Webhook URL to receive complaint notifications
- `ALLOWED_ORIGINS`: Comma-separated list of allowed frontend URLs (optional, defaults to localhost:5173)

### Frontend (.env)

- `VITE_API_URL`: Your backend API URL (defaults to http://localhost:8000)

## Database Schema

The `complaints` table in Supabase contains:
- `id`: Primary key (BIGSERIAL)
- `name`: Reporter's name (TEXT)
- `issue_type`: Type of issue - Garbage, Water, Road, Streetlight, Drainage, Others (TEXT)
- `location`: Address or location of issue (TEXT)
- `description`: Detailed description (TEXT)
- `phone`: Contact phone number (TEXT)
- `timestamp`: When the complaint was registered (TIMESTAMPTZ)

## Webhook Integration

After storing each complaint in Supabase, the backend automatically triggers a webhook (if configured). The webhook sends a POST request with the following JSON payload:

```json
{
  "name": "John Doe",
  "issue_type": "Garbage",
  "location": "123 Main Street",
  "description": "Garbage not collected for 3 days",
  "phone": "1234567890",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### Setting Up Webhooks

1. **Get a Webhook URL**: Use services like:
   - [webhook.site](https://webhook.site) for testing
   - [Zapier](https://zapier.com) for automation
   - [Make.com](https://make.com) for integrations
   - Your own custom endpoint

2. **Configure Environment Variable**:
   - Add `WEBHOOK_URL` to your `.env` file (local) or Render environment variables (production)
   - Example: `WEBHOOK_URL=https://your-webhook-endpoint.com/complaints`

3. **Webhook Behavior**:
   - Webhook is triggered **after** successful storage in Supabase
   - Uses HTTP POST method
   - Timeout: 10 seconds
   - Errors are logged but don't affect the API response
   - If `WEBHOOK_URL` is not set, webhook functionality is skipped silently

## AI Behavior

The AI Community Helpdesk Assistant:
- Acts as a polite digital receptionist
- Guides users through a structured conversation flow
- Validates user inputs (phone numbers, issue types)
- Provides clear confirmation before saving
- Handles errors gracefully

## Issue Types

The system supports the following issue types:
- **Garbage**: Waste collection issues
- **Water**: Water supply problems
- **Road**: Road maintenance issues
- **Streetlight**: Streetlight problems
- **Drainage**: Drainage issues
- **Others**: Any other community issues

## Troubleshooting

### Backend Issues

1. **Import errors**: Make sure all dependencies are installed (`pip install -r requirements.txt`)
2. **Supabase connection errors**: Verify your Supabase URL and key
3. **OpenAI errors**: Check your API key and account credits
4. **Session errors**: Sessions are stored in-memory. For production, consider using Redis

### Frontend Issues

1. **API connection errors**: Verify `VITE_API_URL` is correct
2. **CORS errors**: Update backend `ALLOWED_ORIGINS` environment variable
3. **Build errors**: Check Node.js version (18+)

### Deployment Issues

1. **Render deployment fails**: Check build logs and environment variables
2. **Vercel build fails**: Verify build command and Node.js version
3. **API not accessible**: Check Render service status and URL
4. **Session not persisting**: This is expected - sessions are in-memory. For production, implement Redis or database-backed sessions

## License

MIT License

## Support

For issues or questions, please open an issue on GitHub.
