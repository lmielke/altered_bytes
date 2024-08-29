@echo off
timeout /t 10 /nobreak
powershell -ExecutionPolicy Bypass -File "%altered_bytes%\altered\resources\startup\ollama_run.ps1"
