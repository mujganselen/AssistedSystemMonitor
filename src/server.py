from fastmcp import FastMCP
import psutil
from datetime import datetime
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.firebase_logger import FirebaseLogger, start_background_logging
except ImportError:
    from firebase_logger import FirebaseLogger, start_background_logging
key_path = os.path.join(project_root, "firebase-key.json")
logger = FirebaseLogger(key_path=key_path)
start_background_logging(logger, interval=300) # Log every 5 minutes

from typing import Dict, Any, List

mcp = FastMCP("System Monitor")

def bytes_to_mb(bytes_value: int) -> float:
    """Convert bytes to megabytes."""
    return round(bytes_value / (1024 * 1024), 2)

def bytes_to_gb(bytes_value: int) -> float:
    """Convert bytes to gigabytes."""
    return round(bytes_value / (1024 * 1024 * 1024), 2)

@mcp.tool()
def get_cpu_info() -> dict:
    """Get current CPU usage statistics."""
    try:
        return {
            "overall_percent": psutil.cpu_percent(interval=1),
            "per_core": psutil.cpu_percent(interval=1, percpu=True),
            "core_count": psutil.cpu_count(),
            "physical_cores": psutil.cpu_count(logical=False)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_memory_info() -> dict:
    """Get current RAM usage statistics."""
    try:
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent": mem.percent
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_disk_info() -> dict:
    """Get disk usage statistics. """
    try:
        disk = psutil.disk_usage(os.path.abspath(os.sep))
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_top_processes(limit: int = 5, sort_by: str = "cpu") -> dict:
    """Get top processes by resource usage."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'cpu_percent': info['cpu_percent'] or 0,
                    'memory_percent': round(info['memory_percent'] or 0, 2)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if sort_by == "memory":
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        else:
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

        return {
            "top_processes": processes[:limit],
            "total_count": len(processes),
            "sorted_by": sort_by
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_process_info(pid: int) -> Dict[str, Any]:
    """Get detailed information about a specific process by PID."""
    try:
        proc = psutil.Process(pid)

        return {
            "pid": proc.pid,
            "name": proc.name(),
            "status": proc.status(),
            "cpu_percent": proc.cpu_percent(interval=0.1),
            "memory_percent": round(proc.memory_percent(), 2),
            "memory_mb": bytes_to_mb(proc.memory_info().rss),
            "num_threads": proc.num_threads(),
            "username": proc.username(),
            "create_time": datetime.fromtimestamp(proc.create_time()).isoformat(),
            "cmdline": " ".join(proc.cmdline()[:3]) if proc.cmdline() else "",
            "timestamp": datetime.now().isoformat()
        }
    except psutil.NoSuchProcess:
        return {"error": f"Process with PID {pid} not found"}
    except psutil.AccessDenied:
        return {"error": f"Access denied to process {pid}"}

@mcp.tool()
def search_process_by_name(name: str) -> List[Dict[str, Any]]:
    """Search for processes by name."""
    matching_processes = []

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            if name.lower() in proc.info['name'].lower():
                pinfo = proc.info
                pinfo['cpu_percent'] = round(proc.cpu_percent(interval=0.1), 2)
                pinfo['memory_percent'] = round(pinfo['memory_percent'], 2)
                matching_processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return matching_processes

@mcp.tool()
def get_system_summary() -> Dict[str, Any]:
    """Get a quick overview of the entire system. System summary including CPU, memory, disk, process count, and boot time"""
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(os.path.abspath(os.sep))

    return {
        "cpu_usage_percent": cpu,
        "memory_usage_percent": mem.percent,
        "memory_available_gb": bytes_to_gb(mem.available),
        "disk_usage_percent": disk.percent,
        "disk_free_gb": bytes_to_gb(disk.free),
        "total_processes": len(psutil.pids()),
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def get_network_stats() -> Dict[str, Any]:
    """Get network I/O statistics. Network statistics including bytes sent/received, packets, and errors"""
    net = psutil.net_io_counters()

    return {
        "bytes_sent_mb": bytes_to_mb(net.bytes_sent),
        "bytes_recv_mb": bytes_to_mb(net.bytes_recv),
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv,
        "errors_in": net.errin,
        "errors_out": net.errout,
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def terminate_process(pid: int) -> Dict[str, Any]:
    """Terminate a process (forcefully if needed)."""
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        proc.terminate()

        proc.wait(timeout=3)

        return {
            "success": True,
            "message": f"Process {proc_name} (PID: {pid}) successfully terminated",
            "timestamp": datetime.now().isoformat()
        }
    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Process with PID {pid} not found"}
    except psutil.AccessDenied:
        return {"success": False, "error": f"Access denied. Cannot terminate process {pid}"}
    except psutil.TimeoutExpired:
        try:
            proc.kill()
            return {
                "success": True,
                "message": f"Process {pid} forcefully killed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

@mcp.tool()
def suspend_process(pid: int) -> Dict[str, Any]:
    """Suspend a running process."""
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        proc.suspend()

        return {
            "success": True,
            "message": f"Process {proc_name} (PID: {pid}) suspended",
            "timestamp": datetime.now().isoformat()
        }
    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Process with PID {pid} not found"}
    except psutil.AccessDenied:
        return {"success": False, "error": f"Access denied to process {pid}"}

@mcp.tool()
def resume_process(pid: int) -> Dict[str, Any]:
    """Resume a suspended process."""
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        proc.resume()

        return {
            "success": True,
            "message": f"Process {proc_name} (PID: {pid}) resumed",
            "timestamp": datetime.now().isoformat()
        }
    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Process with PID {pid} not found"}
    except psutil.AccessDenied:
        return {"success": False, "error": f"Access denied to process {pid}"}

@mcp.tool()
def get_historical_stats(limit: int = 10) -> list:
    """Get historical system statistics from the cloud database."""
    return logger.get_history(limit=limit)

if __name__ == "__main__":
    mcp.run()