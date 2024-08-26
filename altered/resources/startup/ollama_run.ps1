# ollama_run.ps1
# This runs the our simple intermediate Ollama server in the background on system startup.
#
# lets wait 10 seconds to let the ollama service start first
Start-Sleep -Seconds 30
cd "$env:altered_bytes"
# Start the Python server script in detached mode using pipenv run
Start-Process -FilePath "pipenv" -ArgumentList "run", "python", "./altered/simple_server.py" -WindowStyle Hidden

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

cat 'C:\Users\lars\python_venvs\packages\altered_bytes/altered/resources/startup/ollama_run.ps1'