
# User Readme for altered_bytes Python Template Package

coming soon

<img src="https://drive.google.com/uc?id=1C8LBRduuHTgN8tWDqna_eH5lvqhTUQR4" alt="me_happy" class="plain" height="150px" width="220px">

## Get and Install

```shell
git clone https://github.com/lmielke/altered_bytes.git ./altered_bytes
cd altered_bytes

# on Windows based ollama server do
# This will create a shortcut in the startup folder that automatically runs the 
# simple_server.py script on startup
cp ".ltered
esources\startup\ollama_run.ps1 - Shortcut.lnk" "~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"

# for headless startup see ./altered/resources/startup/ollama_run.ps1
```

# Simple Server

This is a simple HTTP server that connects to the Ollama API. It can handle both `get_embeddings` and `generate` requests. 

**Note**: The server expects a list of messages inside the context's `prompt` or `messages` parameter. The server will process all messages inside this prompt and return a list of responses. The server can be automatically started on the host machine by running the cp command from the 'Get and Install' section.

# Setting Up Docker and OpenWebUI

## 1. Install Docker Desktop

1. **Download Docker Desktop:**
   - Visit the [Docker Desktop for Windows download page](https://www.docker.com/products/docker-desktop).
   - Download the installer.

2. **Install Docker Desktop:**
   - Run the Docker Desktop installer and follow the prompts.
   - Ensure Hyper-V is enabled during installation.
   - After installation, Docker Desktop should start automatically. If it doesn’t, you can start it manually from the Start menu.

3. **Verify Docker Installation:**
   - Open PowerShell as an administrator and run:
     ```powershell
     docker --version
     ```
   - Run a test container to ensure Docker is functioning correctly:
     ```powershell
     docker run hello-world
     ```

## 2. Set Up OpenWebUI with Docker

1. **Run the OpenWebUI Container:**
   - Use the following command to start OpenWebUI on the host machine:
     ```bash
     docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
     ```
   - This command does the following:
     - Runs the container in detached mode (`-d`).
     - Maps port 8080 inside the container to port 3000 on the host machine (`-p 3000:8080`).
     - Adds the host machine's IP to the container's `/etc/hosts` file (`--add-host=host.docker.internal:host-gateway`).
     - Creates a volume for persistent data (`-v open-webui:/app/backend/data`).
     - Names the container `open-webui` and ensures it restarts automatically (`--restart always`).

2. **Verify the Container is Running:**
   - Check the running containers with:
     ```bash
     docker ps
     ```
   - You should see the `open-webui` container with status `Up` and port mapping `0.0.0.0:3000->8080`.

## 3. Configure Firewall Rules

To ensure OpenWebUI is accessible from other machines on your network, you need to create a firewall rule that allows traffic on port 3000.

1. **Create a Firewall Rule:**
   - Run the following PowerShell command to create the firewall rule:

     ```powershell
     New-NetFirewallRule `
         -DisplayName  "Allow OpenWebUI"
         -Description  "Allows inbound traffic to OpenWebUI on port 3000"
         -Direction  "Inbound"
         -Action  "Allow"
         -Protocol  "TCP"
         -LocalPort  3000
         -Profile  "Any"
         -Enabled "True"
     ```

2. **Verify the Firewall Rule:**
   - Ensure that the rule appears in the list of inbound rules and is enabled.

## 4. Access OpenWebUI

- **From the Host Machine:**
  - Open a web browser and go to `http://localhost:3000`.

- **From Another Machine on the Network:**
  - Open a web browser and go to `http://192.168.0.235:3000` (replace `192.168.0.235` with the actual IP address of the host machine if different).

## 5. Setting Up Task Scheduler for Automatic Startup

To ensure that the server starts automatically at system startup, follow these steps:

1. **Open Task Scheduler:**
   - Press `Windows + R`, type `taskschd.msc`, and press `Enter` to open Task Scheduler.

2. **Create a New Task:**
   - In the **Actions** pane, click **Create Task...**.
   - In the **General** tab:
     - **Name**: Enter `"Start Simple Ollama Server"`.
     - **Description**: Enter `"Starts the Simple Ollama Server using ollama_run.ps1"`.
     - **Security options**:
       - Set **User** to `hostname\username`.
       - Select **Run whether user is logged on or not**.
       - Check **Run with highest privileges**.

3. **Set the Trigger:**
   - Go to the **Triggers** tab and click **New...**.
   - Set **Begin the task** to **At startup**.
   - Click **OK** to save the trigger.

4. **Define the Action:**
   - Go to the **Actions** tab and click **New...**.
   - Set **Action** to **Start a program**.
   - **Program/script**: Enter `powershell.exe`.
   - **Add arguments (optional)**: Enter:
     ```powershell
     -NoProfile -WindowStyle Hidden -File "%altered_bytes%ltered
esources\startup\ollama_run.ps1"
     ```

5. **Configure Conditions and Settings:**
   - In the **Conditions** tab:
     - Uncheck **Start the task only if the computer is on AC power** if you want the task to run regardless of power status.
   - In the **Settings** tab:
     - Ensure **Allow task to be run on demand** is checked.
     - Check **Run task as soon as possible after a scheduled start is missed**.

6. **Save the Task:**
   - Click **OK** to save the task.
   - Enter the password for the user `hostname\username` when prompted.

7. **Test the Task:**
   - In Task Scheduler, right-click the "Start Simple Ollama Server" task and select **Run** to test it.
   - Confirm that the task runs successfully and that the server starts as expected.

## Troubleshooting

- **Check Logs**: If OpenWebUI is not accessible, check the container logs with:
  ```bash
  docker logs open-webui
  ```
- **Verify Docker is Running**: Ensure Docker Desktop is running and the Docker service is active.
- **Firewall Issues**: Double-check that the firewall rule is correctly configured and that the port is open.

## Conclusion

Following these steps should result in a successful installation and configuration of OpenWebUI on your Windows 11 machine, accessible from other devices on the network. If you encounter any issues, refer to the troubleshooting section or check the Docker and firewall configurations.
