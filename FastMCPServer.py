import asyncio
import psutil
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("System Monitor")

def bytes_to_mb(bytes_value: int) -> float:
    return round(bytes_value / (1024 * 1024), 2)
def bytes_to_gb(bytes_value: int) -> float:
    return round(bytes_value / (1024 * 1024 * 1024), 2)

@mcp.tool()
def get_cpu_usage() -> Dict[str, Any]:
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
    cpu_freq = psutil.cpu_freq()

    return {
        "overall_usage_percent": cpu_percent,
        "cpu_count": cpu_count,
        "per_core_usage": cpu_per_core,
        "current_frequency_mhz": round(cpu_freq.current, 2) if cpu_freq else None,
        "max_frequency_mhz": round(cpu_freq.max, 2) if cpu_freq else None,
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def get_memory_usage() -> Dict[str, Any]:
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_gb": bytes_to_gb(mem.total),
        "used_gb": bytes_to_gb(mem.used),
        "available_gb": bytes_to_gb(mem.available),
        "usage_percent": mem.percent,
        "swap_total_gb": bytes_to_gb(swap.total),
        "swap_used_gb": bytes_to_gb(swap.used),
        "swap_percent": swap.percent,
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def get_disk_usage(path: str = "/") -> Dict[str, Any]:

    disk = psutil.disk_usage(path)

    return {
        "path": path,
        "total_gb": bytes_to_gb(disk.total),
        "used_gb": bytes_to_gb(disk.used),
        "free_gb": bytes_to_gb(disk.free),
        "usage_percent": disk.percent,
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def get_top_processes(limit: int = 5, sort_by: str = "cpu") -> List[Dict[str, Any]]:

    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username']):
        try:
            pinfo = proc.info
            cpu = proc.cpu_percent(interval=0.1)
            pinfo['cpu_percent'] = round(cpu, 2)
            pinfo['memory_percent'] = round(pinfo['memory_percent'], 2)
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if sort_by == "cpu":
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    elif sort_by == "memory":
        processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    elif sort_by == "name":
        processes.sort(key=lambda x: x['name'].lower())

    return processes[:limit]


@mcp.tool()
def get_process_info(pid: int) -> Dict[str, Any]:

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
            "cmdline": " ".join(proc.cmdline()[:3]),  # İlk 3 argüman
            "timestamp": datetime.now().isoformat()
        }
    except psutil.NoSuchProcess:
        return {"error": f"Process with PID {pid} not found"}
    except psutil.AccessDenied:
        return {"error": f"Access denied to process {pid}"}


@mcp.tool()
def search_process_by_name(name: str) -> List[Dict[str, Any]]:

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

    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

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
def terminate_process(pid: int) -> Dict[str, Any]:

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
def get_network_stats() -> Dict[str, Any]:

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


if __name__ == "__main__":
    mcp.run(transport="stdio")