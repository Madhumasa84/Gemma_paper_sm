import os
import sys
import platform
import shutil
import torch

def get_environment_info():
    cuda_avail = torch.cuda.is_available()
    cuda_info = {
        "is_available": cuda_avail,
        "device_count": torch.cuda.device_count() if cuda_avail else 0,
        "device_name": torch.cuda.get_device_name(0) if cuda_avail else None,
        "cuda_version": torch.version.cuda if cuda_avail else None,
    }
    
    total_mem = 0
    free_mem = 0
    if cuda_avail:
        try:
            free_b, total_b = torch.cuda.mem_get_info()
            cuda_info["vram_free_gb"] = round(free_b / (1024**3), 2)
            cuda_info["vram_total_gb"] = round(total_b / (1024**3), 2)
        except Exception:
            pass

    # RAM and Disk
    disk = shutil.disk_usage("/")
    sys_ram_gb = None
    try:
        import psutil
        sys_ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        sys_ram_free_gb = round(psutil.virtual_memory().available / (1024**3), 2)
    except ImportError:
        sys_ram_free_gb = None

    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "cuda": cuda_info,
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "system_ram_gb": sys_ram_gb,
        "system_ram_free_gb": sys_ram_free_gb,
    }

def print_diagnostic_summary():
    info = get_environment_info()
    print("=" * 60)
    print("RUNTIME ENVIRONMENT DIAGNOSTIC REPORT")
    print("=" * 60)
    print(f"Python Version : {info['python_version']}")
    print(f"OS Platform    : {info['platform']}")
    print("\n--- Hardware Resources ---")
    if info['system_ram_gb']:
        print(f"System RAM     : {info['system_ram_free_gb']} GB free / {info['system_ram_gb']} GB total")
    print(f"Disk Space     : {info['disk_free_gb']} GB free / {info['disk_total_gb']} GB total")
    
    print("\n--- GPU & CUDA Diagnostics ---")
    cuda = info["cuda"]
    if cuda["is_available"]:
        print(f"CUDA Status    : AVAILABLE (CUDA {cuda['cuda_version']})")
        print(f"Primary Device : {cuda['device_name']}")
        if "vram_total_gb" in cuda:
            print(f"VRAM Capacity  : {cuda['vram_free_gb']} GB free / {cuda['vram_total_gb']} GB total")
    else:
        print("CUDA Status    : NOT AVAILABLE (Running on CPU)")
    print("=" * 60)
