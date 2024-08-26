# ollama_run.ps1
# This runs the our simple intermediate Ollama server in the background on system startup.
#
Start-Sleep -Seconds 15
# Start logging
$logFile = "C:\Users\lars\python_venvs\packages\altered_bytes\altered\resources\startup\ollama_run.log"
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

# # Uncomment and copy this script to the remote terminal
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


# check if running
#  Get-ScheduledTask -TaskName "Start Simple Ollama Server" | Format-List *
