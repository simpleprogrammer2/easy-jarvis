import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# --- Imports adjusted for new project structure ---
from src.voice import Voice
from src.brain import BrainFactory
from src.executor import Executor
from src.core.config import setup_logging, SYSTEM_STATUS_ONLINE
from src.core.matrix_manager import MatrixManager
from src.modules.reminders import get_apple_reminders
from dotenv import load_dotenv

load_dotenv()
logger = setup_logging("Main")

app = FastAPI(title="easy-jarvis Console")

# --- Globals (Managed via Factory where applicable) ---
brain = BrainFactory.create_brain()
executor = Executor()
voice = Voice()
matrix = MatrixManager()

# Handle template directory
current_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Mount static files
app.mount(
    "/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static"
)

# --- API Endpoints ---


@app.get("/", response_class=HTMLResponse)
async def get_console(request: Request):
    logger.debug("Console requested.")
    # Check if we need a weight update for the "Swipe Sequence"
    needs_weight = matrix.needs_weight_update()

    return templates.TemplateResponse(
        request=request,
        name="console.html",
        context={"status": "Online", "needs_weight": needs_weight},
    )


@app.post("/chat")
async def chat_endpoint(payload: dict = Body(...)):
    user_input = payload.get("text")
    if not user_input:
        logger.warning("Chat request received with no text.")
        raise HTTPException(status_code=400, detail="No input provided")

    logger.info(f"Chat request: {user_input}")

    # 1. Brain Reasoning
    ai_response = await brain.process_command(user_input)

    # 2. Vocal Feedback
    import asyncio

    asyncio.create_task(voice.speak(ai_response["speech"]))

    return JSONResponse(content=ai_response)


@app.post("/matrix/log-habits")
async def log_habits_endpoint(payload: dict = Body(...)):
    """Logs the results of the swipe sequence."""
    success = matrix.log_habits(
        no_phone=payload.get("no_phone", False),
        read_book=payload.get("read_book", False),
        exercise=payload.get("exercise", False),
        meditation=payload.get("meditation", False),
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to log habits")
    return {"status": "Matrix Updated"}


@app.post("/matrix/log-weight")
async def log_weight_endpoint(payload: dict = Body(...)):
    """Logs the daily weight metric."""
    weight = payload.get("weight")
    if weight is None:
        raise HTTPException(status_code=400, detail="No weight provided")

    success = matrix.log_weight(float(weight))
    if not success:
        raise HTTPException(status_code=500, detail="Failed to log weight")
    return {"status": "Weight Logged"}


@app.get("/matrix/habits-history")
async def get_habits_history_endpoint():
    """Fetches the habit logs for the last 7 days."""
    return matrix.get_habits_history(days=7)


@app.get("/api/reminders")
async def get_reminders_endpoint():
    """Fetches active Apple Reminders."""
    return {"reminders": get_apple_reminders()}


@app.post("/execute")
async def execute_endpoint(payload: dict = Body(...)):
    command = payload.get("command")
    if not command:
        logger.warning("Execute request received with no command.")
        raise HTTPException(status_code=400, detail="No command provided")

    logger.info(f"Execution request: {command}")

    # 1. Execute via the Terminal Master
    output = executor.execute(command)

    return JSONResponse(content={"output": output})


@app.get("/health")
async def health():
    return {"status": "JARVIS Systems Active"}


# --- Main Entry ---


def run_server():
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🍱 easy-jarvis: Cinematic Console starting on port {port}...")
    logger.info(SYSTEM_STATUS_ONLINE)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run_server()
