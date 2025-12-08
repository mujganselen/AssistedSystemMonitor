#!/usr/bin/env python3
"""Quick test to verify new tools are working."""

import sys
sys.path.insert(0, 'src')

# Import the module to check what's registered
from server import mcp

# Count registered tools
tools = [attr for attr in dir(mcp) if not attr.startswith('_')]
print(f"\n🔧 FastMCP Server Analysis")
print(f"=" * 50)

# Try to get tool count from mcp object
print(f"\nChecking if new tools exist...")

# Test imports work
try:
    from datetime import datetime
    from typing import Dict, Any, List
    import psutil
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")

# Test helper functions
try:
    from server import bytes_to_mb, bytes_to_gb
    print(f"✅ Helper functions loaded: bytes_to_mb, bytes_to_gb")
    print(f"   Test: 1024 MB = {bytes_to_gb(1024 * 1024 * 1024)} GB")
except Exception as e:
    print(f"❌ Helper functions error: {e}")

# Test that new functions exist
print(f"\n📋 Checking for new tool functions:")
new_tools = [
    'get_process_info',
    'search_process_by_name',
    'get_system_summary',
    'get_network_stats',
    'terminate_process',
    'suspend_process',
    'resume_process'
]

from server import (
    get_cpu_info, get_memory_info, get_disk_info, get_top_processes
)

original_tools = [
    'get_cpu_info',
    'get_memory_info',
    'get_disk_info',
    'get_top_processes'
]

print("\n✅ Original 4 tools:")
for tool in original_tools:
    print(f"   - {tool}")

print("\n🆕 New 7 tools:")
for tool in new_tools:
    try:
        exec(f"from server import {tool}")
        print(f"   ✅ {tool}")
    except ImportError:
        print(f"   ❌ {tool} NOT FOUND")

print(f"\n{'='*50}")
print(f"✅ Total: 11 tools should be available")
print(f"\nTo see them in action, the server needs to be queried by an MCP client.")
print(f"The startup screen won't show the tool list.\n")
