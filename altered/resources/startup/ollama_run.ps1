# ollama_run.ps1
# You can cp the shortcut in this folder to the startup folder to run the server on startup.
# See Readme.md
cd "$env:altered_bytes"
# Start the Python server script in detached mode using pipenv run
Start-Process -FilePath "pipenv" -ArgumentList "run", "python", "./altered/simple_server.py" -WindowStyle Hidden
