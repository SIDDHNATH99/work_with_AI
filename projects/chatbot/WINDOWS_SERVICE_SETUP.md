# CortexChat Windows Service Setup Guide

This guide explains how to run CortexChat as a Windows service using the provided files.

## Files Provided

1. **`run_chatbot.bat`** - Simple batch file to start the chatbot
2. **`production.py`** - Production-ready entry point with logging
3. **`main.py`** - The main chatbot application

## Option 1: Simple Batch File (Recommended for beginners)

1. Double-click `run_chatbot.bat` to start the chatbot
2. The chatbot will be accessible at `http://127.0.0.1:8001`
3. To stop, close the console window or press Ctrl+C

## Option 2: Windows Service using NSSM (Recommended for production)

### Step 1: Download NSSM
1. Download NSSM (Non-Sucking Service Manager) from https://nssm.cc/download
2. Extract the zip file
3. Copy `nssm.exe` from either the `win64` or `win32` folder (depending on your system) to your chatbot directory

### Step 2: Install the Service
Open Command Prompt as Administrator and navigate to your chatbot directory:

```bash
cd /d "D:\AI\work_with_AI\projects\chatbot"
nssm install CortexChat
```

### Step 3: Configure the Service
In the NSSM GUI that appears:

**Application tab:**
- Path: `C:\Python\python.exe` (or wherever your Python is installed)
- Startup directory: `D:\AI\work_with_AI\projects\chatbot`
- Arguments: `production.py`

**Details tab:**
- Display name: CortexChat AI Assistant
- Description: A persistent chatbot with file upload capabilities and conversation memory

**Log on tab:**
- Select "Local System account" (or create a specific user account)

**Shutdown tab:**
- Shutdown delay: 3000 milliseconds (3 seconds)

### Step 4: Start the Service
You can start the service by:
- Clicking "Start service" in the NSSM GUI
- Or running: `nssm start CortexChat`
- Or through Windows Services manager (services.msc)

### Step 5: Verify Installation
1. Open Windows Services manager (services.msc)
2. Find "CortexChat AI Assistant"
3. Status should show "Running"
4. Open browser to `http://127.0.0.1:8001` to verify it's working

## Option 3: Windows Service using Python (Alternative)

If you prefer not to use NSSM, you can create a Windows service using Python:

1. Install pywin32: `pip install pywin32`
2. Create a service script (save as `chatbot_service.py`):

```python
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from pathlib import Path

class ChatbotService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CortexChat"
    _svc_display_name_ = "CortexChat AI Assistant"
    _svc_description_ = "A persistent chatbot with file upload capabilities and conversation memory"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def main(self):
        # Change to the chatbot directory
        os.chdir(Path(__file__).parent.absolute())

        # Import and run the chatbot
        from production import *
        # The uvicorn.run() call in production.py will block until stopped

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ChatbotService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ChatbotService)
```

3. Install the service:
```bash
python chatbot_service.py install
```

4. Start the service:
```bash
python chatbot_service.py start
```

## Configuration Options

You can configure the chatbot using environment variables:

Create a `.env` file in the chatbot directory with:

```
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_MODEL_NAME=mistral-small-2503

# Chatbot Settings
CHAT_HOST=127.0.0.1
CHAT_PORT=8001
CHAT_WORKERS=4

# AI Parameters
AI_TEMPERATURE=0.3
AI_TOP_P=0.9
AI_FREQUENCY_PENALTY=0.1
AI_PRESENCE_PENALTY=0.0
AI_MAX_TOKENS=4096
AI_SYSTEM_PROMPT=You are CortexChat, a highly capable AI assistant...
```

## Troubleshooting

### Service Won't Start
1. Check the logs: Look in the `logs/cortexchat.log` file
2. Verify Python path is correct in NSSM configuration
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. Check that ports 8001 is not already in use

### Chatbot Not Responding
1. Verify the service is running in Services manager
2. Check firewall settings - ensure port 8001 is allowed
3. Try accessing `http://127.0.0.1:8001` directly on the server
4. Check logs for error messages

### Updating the Chatbot
1. Stop the service: `nssm stop CortexChat` or through Services manager
2. Update your files
3. Start the service: `nssm start CortexChat`

## Uninstalling the Service

To remove the service:
```bash
nssm remove CortexChat confirm
```
Or through Python service:
```bash
python chatbot_service.py remove
```