# ollama_run.ps1
# This runs the our simple intermediate Ollama server in the background on system startup.
#
Start-Sleep -Seconds 15
# Start logging
$logFile = "$env:altered_bytes\altered\resources\startup\ollama_run.log"
Start-Transcript -Path $logFile -Append

# Log the current directory and environment variables
Write-Output "Starting ollama_run.ps1 script..."
Write-Output "Timestamp: $(Get-Date)"
Write-Output "Current Directory: $(Get-Location)"
Write-Output "altered_bytes Environment Variable: $env:altered_bytes"

# Ensure the environment variable is set (in case it’s not available in the task context)
if (-not $env:altered_bytes) {
    Write-Output "ERROR: Environment variable 'altered_bytes' is not set."
    Stop-Transcript
    exit 1
}

# Change directory and log the result
try {
    cd "$env:altered_bytes"
    Write-Output "Successfully changed directory to: $(Get-Location)"
} catch {
    Write-Output "ERROR: Failed to change directory to $env:altered_bytes. Exception: $_"
    Stop-Transcript
    exit 1
}

# Start the Python server script in detached mode using pipenv run
try {
    Start-Process -FilePath "pipenv" -ArgumentList "run", "python", "./altered/simple_server.py" -WindowStyle Hidden
    Write-Output "Successfully started the Python server script."
} catch {
    Write-Output "ERROR: Failed to start the Python server script. Exception: $_"
    Stop-Transcript
    exit 1
}

# End logging
Write-Output "ollama_run.ps1 script completed."
Stop-Transcript

# we also start docker in case openWebUi is used
# timeout /t 15
winget uninstall Docker.DockerDesktop
# timeout /t 15
# Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe"
# timeout /t 120
# docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main

# # Creating the task using ps did not work due to credentials problems
# # See manual steps down blow instead.
# # Windows: Define the action to run the ollama_run.ps1 script
# $action = New-ScheduledTaskAction -Execute "powershell.exe" `
#    -Argument "-NoProfile -WindowStyle Hidden -File `'$env:altered_bytes/altered/resources/startup/ollama_run.ps1`'"
# # Define the trigger to run the task at system startup
# $trigger = New-ScheduledTaskTrigger -AtStartup
# # Define the principal to run the task with the highest privileges under the SYSTEM account
# $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" `
#    -LogonType ServiceAccount -RunLevel Highest
# # Register the new scheduled task
# Register-ScheduledTask -TaskName "Start Simple Ollama Server" `
#    -Action $action -Trigger $trigger -Principal $principal `
#    -Description "Starts the Simple Ollama Server using ollama_run.ps1"


# Steps to Set Up and Run the "Start Simple Ollama Server" Task
#
# 1. Open Task Scheduler:
#    - Press `Windows + R`, type `taskschd.msc`, and press `Enter` to open Task Scheduler.
#
# 2. Create a New Task:
#    - In the **Actions** pane, click **Create Task...**.
#    - In the **General** tab:
#      - **Name**: Enter `"Start Simple Ollama Server"`.
#      - **Description**: Enter `"Starts the Simple Ollama Server using ollama_run.ps1"`.
#      - **Security options**:
#        - Set **User** to `WHILE-AI-0\lars`.
#        - Select **Run whether user is logged on or not**.
#        - Check **Run with highest privileges**.
#
# 3. Set the Trigger:
#    - Go to the **Triggers** tab and click **New...**.
#    - Set **Begin the task** to **At startup**.
#    - Click **OK** to save the trigger.
#
# 4. Define the Action:
#    - Go to the **Actions** tab and click **New...**.
#    - Set **Action** to **Start a program**.
#    - **Program/script**: Enter `powershell.exe`.
#    - **Add arguments (optional)**: Enter:
#
#      ```powershell
#      -NoProfile -WindowStyle Hidden -File "%altered_bytes%\altered\resources\startup\ollama_run.ps1"
#      ```
#
#    - Click **OK** to save the action.
#
# 5. Configure Conditions and Settings:
#    - In the **Conditions** tab:
#      - Uncheck **Start the task only if the computer is on AC power** if you want the task to run regardless of power status.
#    - In the **Settings** tab:
#      - Ensure **Allow task to be run on demand** is checked.
#      - Check **Run task as soon as possible after a scheduled start is missed**.
#
# 6. Save the Task:
#    - Click **OK** to save the task.
#    - Enter the password for the user `WHILE-AI-0\lars` when prompted.
#
# 7. Test the Task:
#    - In Task Scheduler, right-click the "Start Simple Ollama Server" task and select **Run** to test it.
#    - Confirm that the task runs successfully and that the server starts as expected.
#
# 8. Run the Task from PowerShell (Optional):
#    - To manually run the task from PowerShell, use:
#
#      ```powershell
#      Start-ScheduledTask -TaskName "Start Simple Ollama Server"
#      ```
#
# Notes:
# - When specifying environment variables in Task Scheduler actions, use the `%VARIABLE_NAME%` syntax (e.g., `%altered_bytes%`).


# check if running
#  Get-ScheduledTask -TaskName "Start Simple Ollama Server" | Format-List *