import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import os
import sys
import json
import importlib
import traceback # Kept as it was in original imports

# --- Logging Setup ---
import logging
from pathlib import Path # Original import

# Colorama for colored console output
from colorama import Fore, Style, init as colorama_init

# Initialize Colorama
colorama_init(autoreset=True)

# --- Pre-load your altered_bytes package components ---
import altered.settings as sts
from altered import arguments # Keep if used by contracts or other dependencies
from altered import contracts

# Create a logger instance for this module
module_logger = logging.getLogger(__name__)

def setup_logging():
    """Configures logging for the API server application."""
    if module_logger.hasHandlers() and any(
        isinstance(h, logging.FileHandler) for h in module_logger.handlers
    ):
        return

    module_logger.setLevel(logging.INFO)

    log_dir = Path(sts.logs_dir) / "server"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "api_server_app.log"

        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - '
            '[%(module)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(formatter)

        module_logger.addHandler(file_handler)
        module_logger.info(
            f"Application logging setup complete. Logging to: {log_file}"
        )

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
        # Using the already f-string formatted print from original
        print(
            f"{Fore.RED}FATAL: Could not set up file logging to "
            f"{log_dir / 'api_server_app.log'}: {e}{Style.RESET_ALL}",
            file=sys.stderr
        )

# Call logging setup early
if hasattr(sts, 'logs_dir'): # Original did not check 'and sts.logs_dir' here
    setup_logging()
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    module_logger.warning(
        "sts.logs_dir not found. Application file logging is disabled. "
        "Using basic console logging."
    )
    # Using the already f-string formatted print from original
    print(
        f"{Fore.YELLOW}Warning: sts.logs_dir not configured. "
        f"Application file logging disabled.{Style.RESET_ALL}",
        file=sys.stderr
    )

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Altered Bytes API Server (Simplified Payload)",
    version=sts.get_version() if hasattr(sts, 'get_version') else "0.0.0"
)

# --- Pydantic Model for Response ---
class APIResponseData(BaseModel):
    response: str | dict | None
    log_path: str | None = None

# --- Server Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    module_logger.info("Altered Bytes FastAPI server starting up...")
    module_logger.info("Server is ready and warmed up!")

# --- Core API Dispatch Logic ---
def dispatch_to_api_module(
    api_name_from_request: str,
    processed_args_from_contracts: dict
) -> dict:
    final_response_data = {"response": None, "log_path": None}
    module_logger.debug(
        f"Dispatching to API module: {api_name_from_request} "
        f"with args: {processed_args_from_contracts}"
    )
    try:
        args_for_api_main = processed_args_from_contracts.copy()
        if 'api' not in args_for_api_main:
            args_for_api_main['api'] = api_name_from_request

        module_name_segment = api_name_from_request
        if not module_name_segment.startswith('api_'):
            module_name_segment = f"api_{module_name_segment}"
        module_to_import = f"altered.{module_name_segment}"

        if hasattr(sts, 'package_dir') and sts.package_dir:
            module_file_path = os.path.join( # Using os.path.join as in original
                sts.package_dir, f"{module_name_segment}.py"
            )
            if not os.path.exists(module_file_path): # Using os.path.exists
                msg = f"API module file not found: {module_file_path}"
                module_logger.error(msg)
                final_response_data["response"] = msg
                return final_response_data
        else:
            module_logger.warning(
                "sts.package_dir not configured. "
                "Cannot pre-check API module file existence."
            )

        module_logger.info(
            f"Server: Attempting to import API module: {module_to_import}"
        )
        api_module = importlib.import_module(module_to_import)
        module_logger.info(f"Server: Successfully imported {module_to_import}")

        if hasattr(api_module, "main"):
            module_logger.info(f"Server: Calling {module_to_import}.main()...")
            module_output = api_module.main(**args_for_api_main)
            # Breaking long log message
            log_msg_output = str(module_output)
            if len(log_msg_output) > 70: # Heuristic for shortening display
                log_msg_output = log_msg_output[:67] + "..."
            module_logger.info(
                f"Output from {module_to_import}.main(): {log_msg_output}"
            )

            if isinstance(module_output, str):
                app_type = args_for_api_main.get('application', '').lower()
                is_json_expected = any(
                    keyw in app_type for keyw in ['sublime', 'voice']
                )
                if is_json_expected:
                    try:
                        data = json.loads(module_output)
                        if isinstance(data, dict) and \
                           "response" in data and "log_path" in data:
                            final_response_data = data
                        else:
                            msg = (
                                f"Output from {module_to_import} (JSON expected) "
                                f"was not a valid response dict: {module_output}"
                            )
                            module_logger.warning(msg)
                            final_response_data["response"] = msg
                    except json.JSONDecodeError:
                        msg = (
                            f"Output from {module_to_import} (JSON expected) "
                            f"was a non-JSON string: {module_output}"
                        )
                        module_logger.warning(msg)
                        final_response_data["response"] = msg
                else:
                    final_response_data["response"] = module_output
            elif isinstance(module_output, dict) and \
                 "response" in module_output and "log_path" in module_output:
                final_response_data = module_output
            else:
                msg = (
                    f"Unexpected output from {module_to_import}.main(): "
                    f"{str(module_output)}"
                )
                module_logger.warning(msg)
                final_response_data["response"] = msg
        else:
            msg = f"API module '{module_to_import}' has no main() function."
            module_logger.error(msg)
            final_response_data["response"] = msg
        return final_response_data # Original position: end of try block
    except FileNotFoundError as e:
        msg = f"API module file not found for '{api_name_from_request}': {e}"
        module_logger.error(msg, exc_info=True)
        final_response_data["response"] = msg
        return final_response_data
    except ImportError as e:
        msg = f"Failed to import API module for '{api_name_from_request}': {e}"
        module_logger.error(msg, exc_info=True)
        final_response_data["response"] = msg
        return final_response_data
    except Exception as e:
        msg = (
            f"Error dispatching to API module '{api_name_from_request}': "
            f"{type(e).__name__} - {e}"
        )
        module_logger.error(msg, exc_info=True)
        final_response_data["response"] = msg
        return final_response_data

# --- API Endpoint (Modified) ---
@app.post("/call/", response_model=APIResponseData)
async def handle_api_call(payload: dict = Body(...)):
    """
    Endpoint to receive API call requests as a raw JSON dictionary,
    process them using altered_bytes logic, and return the result.
    ASSUMES CLIENT SENDS CORRECTLY STRUCTURED AND TYPED DATA.
    """
    module_logger.info(
        f"Received API call to /call/ with payload: {payload}"
    )
    try:
        args_as_dict = payload
        api_name_for_call = args_as_dict.get('api_name')
        if not api_name_for_call:
            module_logger.error("Server Error: 'api_name' missing in payload.")
            raise HTTPException(
                status_code=400, detail="'api_name' field is required."
            )

        verbose_level = args_as_dict.get('verbose', 0)
        if not isinstance(verbose_level, int):
            module_logger.error(
                f"Server Error: 'verbose' must be an integer. Got: {verbose_level}"
            )
            raise HTTPException(
                status_code=400, detail="'verbose' field must be an int."
            )

        kwargs_for_checks = args_as_dict.copy()
        kwargs_for_checks.pop('verbose', None)
        kwargs_for_checks.pop('api_name', None)

        module_logger.info(
            f"Server: Processing API call for '{api_name_for_call}'..."
        )
        processed_args = contracts.checks(
            api_name_for_call, verbose=verbose_level, **kwargs_for_checks
        )
        module_logger.info(
            f"Server: Args after contracts.checks: {processed_args}"
        )

        result_data_dict = dispatch_to_api_module(
            api_name_for_call, processed_args
        )

        response_content = result_data_dict.get("response")
        error_keys = ["Error:", "Failed to import", "not found", "Unexpected output"]
        if isinstance(response_content, str) and any(
            err_key in response_content for err_key in error_keys
        ):
            module_logger.warning(
                f"Server: Error flagged by dispatch: {response_content}"
            )
            # Assuming response_content is already a suitable detail string
            raise HTTPException(status_code=400, detail=response_content)

        module_logger.info(
            f"Successfully processed API call for '{api_name_for_call}'."
        )
        return APIResponseData(**result_data_dict)

    except HTTPException:
        module_logger.warning("HTTPException in handle_api_call.", exc_info=True)
        raise
    except Exception as e:
        error_type = type(e).__name__
        module_logger.error(
            f"Server Error (Unexpected Exception in handle_api_call): "
            f"{error_type} - {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {error_type} - Check server logs."
        )

# --- Server Execution ---
def main(*args, **kwargs):
    """
    Entry point for starting the FastAPI server when called via 'alter server'.
    """
    module_logger.info("Attempting to start Altered Bytes API server via main()...")

    server_port = int(os.environ.get("ALTERED_BYTES_PORT", 8777))
    server_host = os.environ.get("ALTERED_BYTES_HOST", "127.0.0.1")

    app_import_string = "altered.api_server:app"

    module_logger.info(
        f"Starting Uvicorn server for '{app_import_string}' on "
        f"http://{server_host}:{server_port}"
    )
    uvicorn.run(
        app_import_string,
        host=server_host,
        port=server_port,
        reload=False,
        log_config=None
    )

if __name__ == "__main__":
    if not (hasattr(sts, 'logs_dir') and module_logger.hasHandlers()):
        if hasattr(sts, 'logs_dir'):
            setup_logging()
        else:
            module_logger.warning(
                "sts.logs_dir not found when running as __main__. "
                "Application file logging is disabled."
            )
            print(
                f"{Fore.YELLOW}Warning: sts.logs_dir not configured. "
                f"File logging disabled.{Style.RESET_ALL}",
                file=sys.stderr
            )

    module_logger.info("Executing api_server.py directly...")

    server_port = int(os.environ.get("ALTERED_BYTES_PORT", 8777))
    server_host = os.environ.get("ALTERED_BYTES_HOST", "127.0.0.1")
    app_import_string = "altered.api_server:app"

    # Corrected log message to reflect reload=False as per original code.
    module_logger.info(
        f"Starting Uvicorn dev server for '{app_import_string}' on "
        f"http://{server_host}:{server_port} (reload=False)."
    )
    uvicorn.run(
                    app_import_string,
                    host=server_host,
                    port=server_port,
                    reload=False, # Kept reload=False as in original code block
                    log_config=None
    )