from fastmcp import FastMCP
import psutil

# Initialize FastMCP server
mcp = FastMCP("System Monitor")

@mcp.tool()
def get_cpu_info() -> dict:
    """Get current CPU usage statistics.

        Returns:
        dict: CPU usage information including overall and per-core percentages
    """
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
    """Get current RAM usage statistics.

    Returns:
        dict: Memory information including total, available, used, and percentage
    """
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
    """Get disk usage statistics.

    Returns:
        dict: Disk information including total, used, free space and percentage
    """
    try:
        disk = psutil.disk_usage('/')
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
    """Get top processes by resource usage.

    Args:
        limit: Number of top processes to return (default: 5)
        sort_by: Sort by 'cpu' or 'memory' (default: 'cpu')

    Returns:
        dict: List of top processes with PID, name, CPU%, and memory%
    """
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

        # Sort processes
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

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()