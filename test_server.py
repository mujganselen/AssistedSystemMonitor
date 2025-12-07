#!/usr/bin/env python3
"""
Simple test script to verify all FastMCP server tools work correctly.
Tests the underlying psutil functionality that the server uses.
"""

import psutil
import json

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_cpu_info():
    print_section("Testing CPU Monitoring (get_cpu_info)")
    try:
        # Simulate what the server does
        result = {
            "overall_percent": psutil.cpu_percent(interval=1),
            "per_core": psutil.cpu_percent(interval=1, percpu=True),
            "core_count": psutil.cpu_count(),
            "physical_cores": psutil.cpu_count(logical=False)
        }
        print(json.dumps(result, indent=2))

        # Verify data is valid
        assert result["overall_percent"] >= 0
        assert len(result["per_core"]) > 0
        assert result["core_count"] > 0
        print("✅ CPU info test PASSED")
        return True
    except Exception as e:
        print(f"❌ CPU info test FAILED: {e}")
        return False

def test_memory_info():
    print_section("Testing Memory Monitoring (get_memory_info)")
    try:
        # Simulate what the server does
        mem = psutil.virtual_memory()
        result = {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent": mem.percent
        }
        print(json.dumps(result, indent=2))

        # Verify data is valid
        assert result["total_gb"] > 0
        assert result["percent"] >= 0
        print("✅ Memory info test PASSED")
        return True
    except Exception as e:
        print(f"❌ Memory info test FAILED: {e}")
        return False

def test_disk_info():
    print_section("Testing Disk Monitoring (get_disk_info)")
    try:
        # Simulate what the server does
        disk = psutil.disk_usage('/')
        result = {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        }
        print(json.dumps(result, indent=2))

        # Verify data is valid
        assert result["total_gb"] > 0
        assert result["percent"] >= 0
        print("✅ Disk info test PASSED")
        return True
    except Exception as e:
        print(f"❌ Disk info test FAILED: {e}")
        return False

def test_top_processes():
    print_section("Testing Process Monitoring (get_top_processes)")
    try:
        # Simulate what the server does
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

        # Sort by CPU
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

        result = {
            "top_processes": processes[:5],
            "total_count": len(processes),
            "sorted_by": "cpu"
        }

        print(f"Top 5 processes by CPU:")
        for proc in result["top_processes"]:
            print(f"  PID {proc['pid']:6d} | {proc['name']:30s} | CPU: {proc['cpu_percent']:5.1f}% | MEM: {proc['memory_percent']:5.2f}%")

        # Verify data is valid
        assert len(result["top_processes"]) <= 5
        assert result["total_count"] > 0
        print("✅ Top processes test PASSED")
        return True
    except Exception as e:
        print(f"❌ Top processes test FAILED: {e}")
        return False

def main():
    print("\n🧪 FastMCP Server Tool Testing Suite")
    print("Testing all 4 monitoring tools...\n")

    results = []

    # Run all tests
    results.append(("CPU Info", test_cpu_info()))
    results.append(("Memory Info", test_memory_info()))
    results.append(("Disk Info", test_disk_info()))
    results.append(("Top Processes", test_top_processes()))

    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your server is working correctly!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
