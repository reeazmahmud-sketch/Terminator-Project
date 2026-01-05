import os
import sys
import time
import json
import pty
import signal
import threading
import psutil
import re
from datetime import datetime
from collections import deque

# --- CONFIGURATION ---
TARGET_SCRIPT = "terminator_universal_cli.py"
LOG_DIR = ".logs"
OBSERVER_LOG_FILE = os.path.join(LOG_DIR, f"TERMINATOR_OBSERVER_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
ANOMALY_PATTERNS = [
    r"Traceback \(most recent call last\)",
    r"Error:",
    r"Exception:",
    r"Fatal",
    r"CRITICAL"
]
RESOURCE_SAMPLE_INTERVAL = 1.0  # Seconds

# --- STATE ---
metrics = {
    "start_time": datetime.now().isoformat(),
    "end_time": None,
    "duration_seconds": 0,
    "exit_code": None,
    "resource_usage": [],
    "anomalies": [],
    "output_bytes": 0,
    "output_lines": 0
}

# Buffer for line-based analysis
line_buffer = ""

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def detect_anomalies(text_chunk):
    global line_buffer
    line_buffer += text_chunk
    
    while '\n' in line_buffer:
        line, line_buffer = line_buffer.split('\n', 1)
        metrics["output_lines"] += 1
        
        # Check for patterns
        for pattern in ANOMALY_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                anomaly = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "PatternMatch",
                    "pattern": pattern,
                    "content": line.strip()
                }
                metrics["anomalies"].append(anomaly)
                # Alert to stderr (observer output, separate from CLI)
                sys.stderr.write(f"\n[OBSERVER ALERT] Anomaly detected: {line.strip()}\n")

def monitor_resources(pid, stop_event):
    """Monitors CPU, Memory, and other resources of the target process."""
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return

    while not stop_event.is_set():
        try:
            # Capture metrics
            with proc.oneshot():
                cpu_percent = proc.cpu_percent(interval=None)
                mem_info = proc.memory_info()
                io_counters = proc.io_counters() if hasattr(proc, 'io_counters') else None
                num_threads = proc.num_threads()
                
            sample = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_rss_mb": mem_info.rss / (1024 * 1024),
                "memory_vms_mb": mem_info.vms / (1024 * 1024),
                "threads": num_threads,
                "read_bytes": io_counters.read_bytes if io_counters else 0,
                "write_bytes": io_counters.write_bytes if io_counters else 0
            }
            metrics["resource_usage"].append(sample)
            
            # Simple threshold check (Example: > 80% CPU alert)
            if cpu_percent > 80:
                 metrics["anomalies"].append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "HighCPU",
                    "value": cpu_percent
                 })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            break
        except Exception as e:
            # Keep monitoring thread alive if possible
            pass
            
        time.sleep(RESOURCE_SAMPLE_INTERVAL)

def master_read(fd):
    """Reads from the child process (Terminator CLI) and passes to stdout + analysis."""
    try:
        data = os.read(fd, 1024)
        if data:
            metrics["output_bytes"] += len(data)
            # Pass to stdout so user sees it
            os.write(sys.stdout.fileno(), data)
            
            # Analyze (decode safely)
            try:
                text_chunk = data.decode('utf-8', errors='replace')
                detect_anomalies(text_chunk)
            except:
                pass 
        return data
    except OSError:
        return b""

def signal_handler(sig, frame):
    # Graceful shutdown on SIGTERM
    raise KeyboardInterrupt

def main():
    ensure_log_dir()
    print(f"[OBSERVER] Starting Terminator CLI Observer...")
    print(f"[OBSERVER] Logging to: {OBSERVER_LOG_FILE}")
    print(f"[OBSERVER] Metrics: CPU, Memory, I/O, Output Patterns")
    print("-" * 60)

    # Prepare command
    cmd = [sys.executable, TARGET_SCRIPT]
    
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        pid, fd = pty.fork()
    except OSError as e:
        print(f"[OBSERVER] Error forking pty: {e}")
        return

    if pid == 0:
        # CHILD PROCESS
        try:
            os.execv(sys.executable, [sys.executable, TARGET_SCRIPT])
        except Exception as e:
            print(f"Failed to exec: {e}")
            sys.exit(1)
    else:
        # PARENT PROCESS (Observer)
        stop_monitor = threading.Event()
        monitor_thread = threading.Thread(target=monitor_resources, args=(pid, stop_monitor))
        monitor_thread.start()

        try:
            # Read loop
            while True:
                try:
                    data = master_read(fd)
                    if not data:
                        break
                except OSError:
                    break
        except (KeyboardInterrupt, OSError):
            pass
        
        # Wait for child to exit
        try:
            _, status = os.waitpid(pid, 0)
            exit_code = os.waitstatus_to_exitcode(status) if hasattr(os, 'waitstatus_to_exitcode') else (status >> 8)
            metrics["exit_code"] = exit_code
        except ChildProcessError:
            metrics["exit_code"] = "Unknown"

        metrics["end_time"] = datetime.now().isoformat()
        start_ts = datetime.fromisoformat(metrics["start_time"])
        end_ts = datetime.fromisoformat(metrics["end_time"])
        metrics["duration_seconds"] = (end_ts - start_ts).total_seconds()
        
        # Stop monitoring
        stop_monitor.set()
        monitor_thread.join()

        # Save Report
        with open(OBSERVER_LOG_FILE, 'w') as f:
            json.dump(metrics, f, indent=2)

        print(f"\n\n[OBSERVER] Session ended. Log saved to {OBSERVER_LOG_FILE}")
        
        # Print summary
        cpu_avg = 0
        if metrics["resource_usage"]:
            cpu_avg = sum(m["cpu_percent"] for m in metrics["resource_usage"]) / len(metrics["resource_usage"])
        
        print(f"[OBSERVER] Summary:")
        print(f"  Duration: {metrics['duration_seconds']:.2f}s")
        print(f"  Avg CPU:  {cpu_avg:.1f}%")
        print(f"  Peak RSS: {max((m['memory_rss_mb'] for m in metrics['resource_usage']), default=0):.1f} MB")
        print(f"  Anomalies: {len(metrics['anomalies'])}")

if __name__ == "__main__":
    main()