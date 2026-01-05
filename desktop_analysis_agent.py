#!/usr/bin/env python3
import os
import subprocess
import csv
from datetime import datetime
from pathlib import Path

DESKTOP_PATH = os.path.expanduser("~/Desktop")
OUTPUT_FILE = os.path.join(os.getcwd(), "desktop_analysis_report.csv")

def get_folder_size(path):
    """Get folder size using du -sh"""
    try:
        # -k for kilobytes to make sorting easier, or -h for human readable
        # Using -s for summary of the directory
        cmd = ["du", "-sh", path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.split()[0]
    except Exception:
        pass
    return "N/A"

def get_file_count(path):
    """Count files recursively using find"""
    try:
        # find . -type f | wc -l
        cmd = ["find", path, "-type", "f"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    except Exception:
        pass
    return 0

def get_last_modified(path):
    """Get last modified date of the folder"""
    try:
        timestamp = os.path.getmtime(path)
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "N/A"

def scan_desktop():
    print(f"🔍 Scanning Desktop folders at {DESKTOP_PATH}...")
    
    results = []
    
    # Iterate over items in Desktop
    for item in os.listdir(DESKTOP_PATH):
        # Exclusions: Hidden files/folders and system files
        if item.startswith('.') or item.startswith('$') or item == "Icon\r":
            continue
            
        full_path = os.path.join(DESKTOP_PATH, item)
        
        if os.path.isdir(full_path):
            print(f"  • Analyzing: {item}")
            size = get_folder_size(full_path)
            count = get_file_count(full_path)
            mod_date = get_last_modified(full_path)
            
            results.append({
                "Folder Name": item,
                "Size": size,
                "File Count": count,
                "Last Modified": mod_date,
                "Path": full_path
            })

    # Write to CSV
    print(f"\n📝 Generating report: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', newline='') as csvfile:
        fieldnames = ["Folder Name", "Size", "File Count", "Last Modified", "Path"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in results:
            writer.writerow(row)
            
    print("✅ Analysis complete.")

if __name__ == "__main__":
    scan_desktop()
