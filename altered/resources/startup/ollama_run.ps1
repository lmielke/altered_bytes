# Change to the directory where your Pipenv environment and simple_server.py are located
cd "$env:altered_bytes"
# Start the Python server script in detached mode using pipenv run
Start-Process -FilePath "pipenv" -ArgumentList "run", "python", "./alter/simple_server.py" -WindowStyle Hidden
