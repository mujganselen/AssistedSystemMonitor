# LLM-Assisted System Monitor

An intelligent system monitor that uses FastMCP to expose OS metrics to LLM clients for natural language querying.

## Team Members
- Nermin Tunçbilek
- Menekşe Uzunçelebi
- Müjgan Selen Karakaş

## Features
- **Real-time Monitoring**: CPU (overall and per-core), RAM, and Disk space tracking.
- **Process Control**: Search, terminate, suspend, and resume processes directly via natural language.
- **Cloud Logging**: Automatic background logging of performance metrics to Firebase Firestore.
- **Historical Analysis**: Retrieve and analyze historical performance trends from the cloud.
- **Natural Language Interface**: Fully integrated with FastMCP for interaction via Cursor or other LLM clients.

## Installation

1. **Clone the repository** (or navigate to project directory)
```bash
cd "AssistedSystemMonitor"
```

2. **Set up Virtual Environment** (Recommended)
   It prevents dependency conflicts with your system python.
```bash
# Create virtual environment
python3 -m venv venv

# Activate it macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
# .\venv\Scripts\activate
```

3. **Setup Firebase**
   - Place your `firebase-key.json` in the root directory.
   - The system will automatically use it for cloud logging.

4. **Install dependencies**
```bash
pip install -r requirements.txt
```


### Cursor IDE Integration
You should configure Cursor to recognize the local MCP server:

1.  **Install Cursor**: Download and install from https://cursor.com/download.
2.  **Configure MCP Server**:
    - Go to **Cursor Settings** > **Tools & MCP** 
    - Click **New MCP Server**.
    - **Name**: `System Monitor` (or any name you prefer).
    - **Type**: `stdio`. (if asked)
    
   You must use absolute paths for both the python executable (in your venv) and the server.py script.
   Configuration Template (mcp.json):

   {
      "mcpServers": {
         "Assisted System Monitor": {
            "command": "/ABSOLUTE/PATH/TO/PROJECT/venv/bin/python",
            "args": [
               "/ABSOLUTE/PATH/TO/PROJECT/src/server.py"
            ]
         }
      }
   }

3.  **Enable**: Toggle the switch to enable the server.
4.  **Chat**: Open a new chat compatible with "Agent Mode" and ask questions like "Check my CPU usage".


## Usage

Once added in Cursor settings, ensure the status indicator turns Green.

Open Cursor Chat (Cmd+L) and ask questions like:

"What is my current CPU usage?"

"Find the process consuming the most memory."

"Show me the system performance trend for the last 1 hour." (The server logs system stats to Firebase in the background periodically. For trend analysis queries (like "last 1 hour") to work effectively, the server must have been running for at least 1 hour to accumulate sufficient log data.)

### Key Tools
1. `get_system_summary()` - Quick overview of entire system status.
2. `get_top_processes()` - List resource-heavy processes.
3. `terminate_process(pid)` - Stop a specific process.
4. `get_historical_stats()` - Pull history from Firebase.

## Project Structure
```
AssistedSystemMonitor/
├── src/
│   ├── firebase_logger.py # Firebase integration
│   └── server.py          # Main FastMCP server
├── firebase-key.json      # Firebase credentials (not in git)
├── requirements.txt       # Dependencies
├── .gitignore             # Git ignore patterns
└── README.md              # This file
```