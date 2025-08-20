# api_server.py
# for logging set module_logger.setLevel(logging.INFO) to DEBUG
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import importlib, json, logging, os, pyttsx3, sys
from pathlib import Path
from colorama import Fore, Style

# --- Pre-load your altered_bytes package components ---
# These are assumed to be in the python path
import altered.settings as sts

# Create a logger instance for this module
module_logger = logging.getLogger(__name__)
if hasattr(sts, 'logs_dir'):
    logs_dir = sts.logs_dir
else:
    logs_dir = os.getcwd()
log_dir = Path(logs_dir) / "server"
log_name = "api_server.log"
log_file = log_dir / log_name

def _speak_message(message: str, *args, **kwargs):
    """Uses pyttsx3 to speak a given message."""
    try:
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        logging.error(f"Text-to-speech failed: {e}")

async def _preload_on_startup(*args, **kwargs) -> None:
    """
    Fires a self-call to /call to warm up models/caches.
    Why: ensures Ollama/model path is loaded before first request.
    """
    payload = {'api': 'thought', 'kwargs_defaults': 'fast_api_pre_load'}
    try:
        res = await handle_api_call(payload)
        module_logger.debug(f"Preload OK: {res}")
    except Exception:
        module_logger.error("Preload failed", exc_info=True)

def setup_logging():
    """Configures logging for the API server application."""
    if module_logger.hasHandlers() and any(
        isinstance(h, logging.FileHandler) for h in module_logger.handlers
    ):
        return

    module_logger.setLevel(logging.INFO)
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
                                                '%(asctime)s - %(name)s - [%(levelname)s] - '
                                                '[%(module)s:%(lineno)d] - %(message)s'
                                    )
        )
        module_logger.addHandler(file_handler)
        module_logger.debug(f"Application logging setup complete. Logging to: {log_file}" )
    except Exception as e:
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        module_logger.error(
            f"Failed to set up file logging for application: {e}. "
            "Using basic console logging for errors.",
            exc_info=True
        )
        print(
            f"{Fore.RED}FATAL: Could not set up file logging to "
            f"{log_dir / 'api_server_app.log'}: {e}{Style.RESET_ALL}",
            file=sys.stderr
        )

# Call logging setup early
setup_logging()
# --- FastAPI Application Setup ---
app = FastAPI(
    title="Altered Bytes API Server (Simplified Payload)",
    version=sts.get_version() if hasattr(sts, 'get_version') else "0.0.0"
)

def check_payload(payload: dict):
    """
    Checks if the payload contains the required 'api' field.
    Raises HTTPException if 'api' is missing.
    """
    module_logger.debug(f"Checking payload: {payload}")
    api = payload.get('api')
    if not api:
        module_logger.error("Payload missing 'api'.")
        raise HTTPException(
            status_code=400,
            detail="'api' field is required in the payload."
        )
    return f"altered.api_{api}"

# --- Pydantic Model for Response ---
class APIResponseData(BaseModel):
    response: str | dict | None
    log_path: str | None = None

# --- Server Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    """Logs server startup, speaks ready message, then preloads via /call."""
    module_logger.debug("Altered Bytes FastAPI server starting up...")
    module_logger.debug("Server is ready and warmed up!")
    port = os.environ.get('port')
    _speak_message(f"Altered Bytes API server is running on port {port}!")
    await _preload_on_startup()

# --- API Endpoint (Simplified) ---
@app.post("/call/", response_model=APIResponseData)
async def handle_api_call(payload: dict = Body(...)):
    """
    Receives a request, dynamically imports the specified API module,
    and executes its main function with the request payload.
    """
    module_logger.debug(f"Received API call with payload: {payload}")
    module_file_name = check_payload(payload)
    try:
        # Construct the full module name to import
        module_logger.debug( 
                            f"Attempting to import and run: {module_file_name} "
                            f"Calling {module_file_name}.main() with {payload = }."
                            )
        # Dynamically import the target module and call it
        result = importlib.import_module(module_file_name).main(**payload)
        # Log the result for debugging
        module_logger.debug(f"Result {result = }")
        # NEW: Handle if the module returns a JSON string
        if isinstance(result, str):
            try:
                result_dict = json.loads(result)
                if isinstance(result_dict, dict) and "response" in result_dict:
                    return APIResponseData(**result_dict)
            except json.JSONDecodeError:
                # Not a JSON string, fall through to default handling
                pass
        # Handle if the module returns a dict directly
        if isinstance(result, dict) and "response" in result:
            return APIResponseData(**result)
        else:
            # If not a dict or valid JSON string, wrap the result.
            return APIResponseData(response=result, log_path=None)
    except ImportError:
        msg = f"API module not found for '{module_file_name =}'."
        module_logger.error(msg, exc_info=True)
        raise HTTPException(status_code=404, detail=msg)
    except Exception as e:
        msg = (
            f"An unexpected error occurred while processing API '{module_file_name =}': "
            f"{type(e).__name__} - {e}"
        )
        module_logger.error(msg, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error for API '{module_file_name =}'. Check logs."
        )


@app.get("/ping")
async def ping() -> dict:
    """Simple health-check endpoint."""
    module_logger.debug("Ping received")
    return {"status": "pong"}

# --- Server Execution ---
def main(*args, **kwargs):
    """
    Entry point for starting the FastAPI server when called via 'alter server'.
    """
    module_logger.debug("Attempting to start Altered Bytes API server via main()...")

    port = int(os.environ.get("port"))
    host = os.environ.get("ALTERED_BYTES_HOST", "127.0.0.1")

    app_import_string = "altered.api_server:app"

    module_logger.debug(
        f"Starting Uvicorn server for '{app_import_string}' on "
        f"http://{host}:{port}"
    )
    uvicorn.run(
        app_import_string,
        host=host,
        port=port,
        reload=False,
        log_config=None
    )
