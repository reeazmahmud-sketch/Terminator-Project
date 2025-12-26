# Red Team Simulator: DKOM Process Hider

This is a **Defensive Training Kernel Module** designed to simulate a rootkit's ability to hide processes. 

**Purpose:** To generate the specific kernel activity (syscall hooking, DKOM) required to test Blue Team tools like eBPF monitors (e.g., Tetragon, Falco).

## How it Works
1.  **Syscall Hook:** It finds the `sys_call_table` and overwrites the pointer for `sys_getdents64` (Directory Listing).
2.  **Filter:** When you run `ls /proc` or `ps`, the hook intercepts the results.
3.  **Hide:** (In full version) It removes the entry matching `target_pid`. (In this safety-locked PoC) It logs "INTERCEPTED" to dmesg to prove control without destabilizing the system.

## Usage (Training)

1.  **Compile:**
    ```bash
    make
    ```

2.  **Start a Dummy Process:**
    ```bash
    sleep 1000 &
    PID=$!
    echo "Target PID: $PID"
    ```

3.  **Load Simulator:**
    ```bash
    sudo insmod dk_hider.ko target_pid="$PID"
    ```

4.  **Verify Detection (Blue Team):**
    *   **Check logs:** `dmesg | tail` should show "SIMULATOR: Hooked sys_getdents64".
    *   **eBPF Check:** Run your eBPF tool. It should flag "Syscall Table Modification" or "Unexpected sys_getdents64 behavior".

5.  **Unload:**
    ```bash
    sudo rmmod dk_hider
    ```

## Safety
This module modifies `CR0` write protection. Use ONLY in a VM.
