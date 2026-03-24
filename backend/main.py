"""
API LAYER (main.py)
-------------------
This is the entry point of our backend. It uses FastAPI to create web endpoints 
that the React frontend can talk to. It acts as a traffic director:
- Graph requests go to the Data Layer (database.py).
- Chat requests go to the Intelligence Layer (agent.py).
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our custom layers
from database import fetch_graph_visualization_data
from agent import process_chat_query

app = FastAPI(title="Context Graph API")

# Setup CORS so the React frontend running on port 5173 can talk to this backend on port 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    """Defines the shape of the data we expect from the frontend chat."""
    query: str

@app.get("/")
def read_root():
    """Friendly welcome message for the root URL."""
    return {"message": "Nexus Context Graph API is running perfectly! Please use the React frontend to interact with the system."}

@app.get("/api/health")
def health_check():
    """Simple endpoint to verify the backend is running."""
    return {"status": "Backend is online and ready."}

@app.get("/api/graph")
def get_graph_data():
    """
    Endpoint for the visual graph on the frontend.
    Fetches nodes and edges from our Data Layer.
    """
    try:
        data = fetch_graph_visualization_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/chat")
def chat_with_agent(request: ChatRequest):
    """
    Endpoint for the AI chat bounding box on the frontend.
    Passes the user's string to our Intelligence Layer.
    """
    try:
        answer = process_chat_query(request.query)
        return {"response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Agent error: {str(e)}")
