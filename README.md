# LLM-Assisted System Monitor

An intelligent system monitor that uses FastMCP to expose OS metrics to LLM clients for natural language querying.

## Team Members
- Nermin Tunçbilek
- Menekşe Uzunçelebi
- Müjgan Selen Karakaş

## Features
- Real-time CPU monitoring
- Memory usage tracking# LLM-Assisted System Monitor

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

2. **Setup Firebase**
   - Place your `firebase-key.json` in the root directory.
   - The system will automatically use it for cloud logging.

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### Running the MCP Server
```bash
python src/server.py
```

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
├── scripts/               # Diagnostic and test scripts
├── firebase-key.json      # Firebase credentials (not in git)
├── requirements.txt        # Dependencies
├── .gitignore             # Git ignore patterns
└── README.md              # This file
```