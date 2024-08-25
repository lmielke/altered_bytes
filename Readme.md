# User Readme for altered_bytes python template package

coming soon

<img src="https://drive.google.com/uc?id=1C8LBRduuHTgN8tWDqna_eH5lvqhTUQR4" alt="me_happy" class="plain" height="150px" width="220px">

## get and install
```shell
    git clone https://github.com/lmielke/altered_bytes.git ./altered_bytes
    cd altered_bytes
    # on Windows based ollama server do
    # This will create a shortcut in the startup folder that automatically runs the 
    # simple_server.py script on startup
    cp ".\altered\resources\startup\ollama_run.ps1 - Shortcut.lnk" "~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
```

# Simple Server
This is a simple http server that connects to the ollama api. It can handle both
get_embeddings and generate requests. 
NOTE: The server expects a list of messages inside the context['prompt'/'messages'] parameter.
The server will process all messages inside this prompt and return a list of responses.
The server can be automatically started on the host machine by running the cp command from 
'get and install' section. 
