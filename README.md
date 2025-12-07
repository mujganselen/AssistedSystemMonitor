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
- Real-time CPU monitoring
- Memory usage tracking
- Disk space monitoring
- Process listing and analysis
- Natural language interface via LLM

## Installation

1. **Clone the repository** (or navigate to project directory)
```bash
cd "AssistedSystemMonitor"
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### Running the MCP Server
```bash
python src/server.py
```

### Available Tools
1. `get_cpu_info()` - Returns CPU usage statistics
2. `get_memory_info()` - Returns RAM usage information
3. `get_disk_info()` - Returns disk usage statistics
4. `get_top_processes(limit, sort_by)` - Returns top processes by CPU or memory

## Configuration

Copy `.env.example` to `.env` and add your OpenAI API key:
```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your_actual_key_here
```

## macOS Permissions

On macOS, you may need to grant Terminal or your IDE accessibility permissions:
1. System Preferences → Security & Privacy → Privacy → Accessibility
2. Add Terminal or your IDE to the allowed apps

## Project Structure
```
AssistedSystemMonitor/
├── src/
│   ├── __init__.py
│   └── server.py          # FastMCP server
├── requirements.txt        # Dependencies
├── .gitignore             # Git ignore patterns
├── .env.example           # Environment template
└── README.md              # This file
```

## Future Enhancements
- Process control (terminate, suspend, resume)
- Cloud database integration for historical data
- Cursor IDE integration
- Advanced natural language queries
```