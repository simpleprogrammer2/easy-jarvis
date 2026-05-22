import asyncio
import os
import sys
import json
import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Handle module path for robust execution
try:
    from src.voice import Voice
    from src.brain import Brain
    from src.executor import Executor
except ImportError:
    from voice import Voice
    from brain import Brain
    from executor import Executor

from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="easy-jarvis Console")

# --- Globals ---
brain = Brain()
executor = Executor()
voice = Voice()

# Handle template directory
current_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def get_console(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="console.html", 
        context={"status": "Online"}
    )

@app.post("/chat")
async def chat_endpoint(payload: dict = Body(...)):
    user_input = payload.get("text")
    if not user_input:
        raise HTTPException(status_code=400, detail="No input provided")
    
    # 1. Brain Reasoning
    ai_response = await brain.process_command(user_input)
    
    # 2. Vocal Feedback (Run in background to avoid blocking the JSON response)
    asyncio.create_task(voice.speak(ai_response['speech']))
    
    return JSONResponse(content=ai_response)

@app.post("/execute")
async def execute_endpoint(payload: dict = Body(...)):
    command = payload.get("command")
    if not command:
        raise HTTPException(status_code=400, detail="No command provided")
    
    # 1. Execute via the Terminal Master
    output = executor.execute(command)
    
    return JSONResponse(content={"output": output})

@app.get("/health")
async def health():
    return {"status": "JARVIS Systems Active"}

# --- Main Entry ---

def run_server():
    port = int(os.getenv("PORT", 8000))
    print(f"🍱 easy-jarvis: Cinematic Console starting on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    run_server()
