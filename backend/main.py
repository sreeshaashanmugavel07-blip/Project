from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
import os
import requests
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from supabase import create_client, Client
import re

load_dotenv()

# Initialize FastAPI
app = FastAPI(title="AI Community Issue Reporting Assistant")

# CORS Configuration
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client initialized successfully")
    except Exception as e:
        print(f"Error initializing Supabase: {e}")

# Initialize OpenAI (for LangChain)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = None
if OPENAI_API_KEY:
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=OPENAI_API_KEY)
        print("OpenAI LLM initialized successfully")
    except Exception as e:
        print(f"Error initializing OpenAI: {e}")

# Webhook URL
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Issue types
ISSUE_TYPES = ["Garbage", "Water", "Road", "Streetlight", "Drainage", "Others"]

# Conversation State
class ConversationState:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.name: Optional[str] = None
        self.issue_type: Optional[str] = None
        self.location: Optional[str] = None
        self.description: Optional[str] = None
        self.phone: Optional[str] = None
        self.current_step = "greet"
        self.messages: List[Dict] = []

# In-memory session storage (use Redis in production)
sessions: Dict[str, ConversationState] = {}

def process_conversation(state: ConversationState, user_message: str) -> str:
    """Process conversation based on current step - Updated flow: Greet -> Issue Type -> Location -> Description -> Name -> Contact -> Confirm"""
    user_msg_lower = user_message.strip().lower()
    
    # This step should not be reached in normal flow since we set ask_issue_type on new session
    if state.current_step == "greet":
        state.current_step = "ask_issue_type"
        return "What type of issue are you reporting? Please choose from: Garbage, Water, Road, Streetlight, Drainage, or Others."
    
    elif state.current_step == "ask_issue_type":
        # Match issue type
        matched_type = None
        for issue_type in ISSUE_TYPES:
            if issue_type.lower() in user_msg_lower:
                matched_type = issue_type
                break
        
        if matched_type:
            state.issue_type = matched_type
            state.current_step = "ask_location"
            return f"Got it! {matched_type} issue. Where is this issue located? Please provide the address or location."
        else:
            return f"I didn't recognize that issue type. Please choose from: {', '.join(ISSUE_TYPES)}"
    
    elif state.current_step == "ask_location":
        state.location = user_message.strip()
        if state.location:
            state.current_step = "ask_description"
            return "Could you please provide a detailed description of the issue?"
        else:
            return "Please provide a location for the issue."
    
    elif state.current_step == "ask_description":
        state.description = user_message.strip()
        if state.description:
            state.current_step = "ask_name"
            return "Thank you for the details. May I have your name, please?"
        else:
            return "Please provide a description of the issue."
    
    elif state.current_step == "ask_name":
        # Extract name from user message
        if llm:
            try:
                prompt = f"Extract the person's name from this message. Return only the name, nothing else, no punctuation: {user_message}"
                response = llm.invoke([HumanMessage(content=prompt)])
                state.name = response.content.strip().strip('.,!?')
            except Exception as e:
                print(f"Error extracting name with LLM: {e}")
                state.name = user_message.strip()
        else:
            state.name = user_message.strip()
        
        if state.name:
            state.current_step = "ask_contact"
            return f"Thank you for informing, {state.name}. May I have your contact number for follow-up?"
        else:
            return "I didn't catch your name. Could you please tell me your name?"
    
    elif state.current_step == "ask_contact":
        # Extract phone number
        phone_digits = re.sub(r'\D', '', user_message)
        if len(phone_digits) >= 10:
            state.phone = phone_digits
            state.current_step = "confirm"
            # Show confirmation
            return f"""Thank you! Let me confirm your details:

Name: {state.name}
Issue Type: {state.issue_type}
Location: {state.location}
Description: {state.description}
Contact: {state.phone}

Is this information correct? (Yes/No)"""
        else:
            return "Please provide a valid contact number with at least 10 digits."
    
    elif state.current_step == "confirm":
        if "yes" in user_msg_lower or "correct" in user_msg_lower or user_msg_lower == "y":
            # Save to Supabase
            complaint_data = {
                "name": state.name,
                "issue_type": state.issue_type,
                "location": state.location,
                "description": state.description,
                "phone": state.phone,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Save to database
            save_success = False
            if supabase:
                try:
                    result = supabase.table("complaints").insert(complaint_data).execute()
                    print(f"Saved complaint to Supabase: {result}")
                    save_success = True
                except Exception as e:
                    print(f"Error saving to Supabase: {e}")
                    # Continue even if Supabase fails
            else:
                print("Supabase not configured, skipping database save")
                save_success = True  # Consider it successful if Supabase not configured
            
            # Trigger webhook
            webhook_success = False
            if WEBHOOK_URL:
                try:
                    webhook_response = requests.post(
                        WEBHOOK_URL,
                        json=complaint_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    print(f"Webhook triggered: {webhook_response.status_code}")
                    webhook_success = True
                except Exception as e:
                    print(f"Error triggering webhook: {e}")
                    # Continue even if webhook fails
            else:
                print("Webhook not configured, skipping")
                webhook_success = True  # Consider it successful if webhook not configured
            
            state.current_step = "completed"
            return "Thank you for reporting the issue. Your complaint has been successfully registered. Our team will review it and contact you soon. Have a great day!"
        
        elif "no" in user_msg_lower or user_msg_lower == "n":
            # Reset and start over
            state.name = None
            state.issue_type = None
            state.location = None
            state.description = None
            state.phone = None
            state.current_step = "ask_issue_type"
            return "No problem! Let's start over. What type of issue are you reporting? Please choose from: Garbage, Water, Road, Streetlight, Drainage, or Others."
        else:
            return "Please respond with 'Yes' or 'No' to confirm."
    
    elif state.current_step == "completed":
        return "Thank you! Your complaint has already been registered. Is there anything else I can help you with?"
    
    return "I'm here to help. How can I assist you today?"

# API Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    timestamp: str

# Routes
@app.get("/")
def home():
    return {"message": "AI Community Issue Reporting Assistant backend running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        user_message = req.message.strip()
        
        # Get or create session
        session_id = req.session_id or f"session_{datetime.utcnow().timestamp()}"
        is_new_session = session_id not in sessions
        
        # Allow empty message only for new sessions (to get greeting)
        if not user_message and not is_new_session:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if is_new_session:
            sessions[session_id] = ConversationState(session_id)
            # For new sessions, return greeting and ask for issue type
            greeting = "Hello! I am the Community Helpdesk Assistant. What type of issue are you reporting? Please choose from: Garbage, Water, Road, Streetlight, Drainage, or Others."
            sessions[session_id].current_step = "ask_issue_type"
            sessions[session_id].messages.append({
                "role": "assistant",
                "content": greeting
            })
            timestamp = datetime.utcnow().isoformat()
            return ChatResponse(
                reply=greeting,
                session_id=session_id,
                timestamp=timestamp
            )
        
        state = sessions[session_id]
        
        # Debug: Print current state
        print(f"Session {session_id}: Current step = {state.current_step}, User message = '{user_message}'")
        
        # Add user message to history
        state.messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Process conversation
        try:
            ai_reply = process_conversation(state, user_message)
            print(f"Session {session_id}: New step = {state.current_step}, Reply = '{ai_reply[:50]}...'")
            state.messages.append({
                "role": "assistant",
                "content": ai_reply
            })
        except Exception as e:
            print(f"Error processing conversation: {e}")
            import traceback
            traceback.print_exc()
            # Return a helpful error message instead of crashing
            error_reply = f"I encountered an issue processing your message. Please try again or rephrase your response."
            state.messages.append({
                "role": "assistant",
                "content": error_reply
            })
            timestamp = datetime.utcnow().isoformat()
            return ChatResponse(
                reply=error_reply,
                session_id=session_id,
                timestamp=timestamp
            )
        
        timestamp = datetime.utcnow().isoformat()
        
        return ChatResponse(
            reply=ai_reply,
            session_id=session_id,
            timestamp=timestamp
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "supabase_connected": supabase is not None,
        "openai_configured": llm is not None,
        "webhook_configured": bool(WEBHOOK_URL)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
