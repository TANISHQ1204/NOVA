import os
import psutil
import platform
import subprocess
import time
from pathlib import Path

SEARCH_DIRS=[
    Path.home()/"Desktop",
    Path.home()/"Downloads",
    Path.home()/"Documents",
    Path.home()/"Pictures",
    Path.home()/"Music",
    Path.home()/"Videos",
]

def get_disk_space():
    disk=psutil.disk_usage('C:/')
    total=round(disk.total/(1024**3),1)
    used=round(disk.used/(1024**3),1)
    free=round(disk.free/(1024**3),1)
    return f"C drive — {total}GB total, {used}GB used, {free}GB free."

def find_file(filename):
    filename=filename.lower()
    results=[]
    for directory in SEARCH_DIRS:
        if not directory.exists():
            continue
        for file in directory.rglob('*'):
            if filename in file.name.lower():
                results.append(file)
    if not results:
        return None, "No file found with that name."
    return results[0], f"Found {results[0].name} in {results[0].parent}"

def open_folder(folder_name):
    folder_map={
        "downloads":Path.home()/"Downloads",
        "desktop":Path.home()/"Desktop",
        "documents":Path.home()/"Documents",
        "pictures":Path.home()/"Pictures",
        "music":Path.home()/"Music",
        "videos":Path.home()/"Videos",
    }
    folder=folder_map.get(folder_name.lower())
    if folder and folder.exists():
        os.startfile(folder)
        return f"Opening {folder_name} folder."
    return f"Couldn't find {folder_name} folder."

def get_recent_files(n=5):
    files=[]
    for directory in SEARCH_DIRS:
        if not directory.exists():
            continue
        for file in directory.rglob('*'):
            if file.is_file():
                files.append((file.stat().st_mtime, file))
    files.sort(reverse=True)
    recent=files[:n]
    if not recent:
        return "No recent files found."
    result="Recent files:\n"
    for mtime,file in recent:
        result+=f"— {file.name}\n"
    return result.strip()

def get_system_info():
    boot_time=psutil.boot_time()
    uptime_seconds=time.time()-boot_time
    uptime_hours=round(uptime_seconds/3600,1)
    return (
        f"OS: {platform.system()} {platform.release()}, "
        f"PC: {platform.node()}, "
        f"Uptime: {uptime_hours} hours."
    )

def open_file(filepath):
    os.startfile(filepath)

