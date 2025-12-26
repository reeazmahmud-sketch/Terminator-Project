<!--
  Terminator Universal Framework
  Architect: Reeaz Mahmud | AI Partner: Gemini
  Date: December 17, 2025
-->

# Linux Kernel AI Agent (LKM)

This directory contains a Proof-of-Concept (PoC) for running a lightweight AI agent directly inside the Linux Kernel as a Loadable Kernel Module (LKM).

## Architecture
- **`ai_agent.c`**: The kernel module. Implements a fixed-point inference engine (simple linear model with ReLU) and exposes a character device `/dev/ai_agent`.
- **`user_client.c`**: A user-space C program that connects to the kernel agent to send prediction requests and update model weights.
- **`Makefile`**: Standard Kbuild makefile.

## Requirements
- A Linux system (this will not run on macOS/Windows directly).
- Kernel headers installed (`sudo apt install linux-headers-$(uname -r)`).
- GCC and Make.

## How to Run

1.  **Compile the Module:**
    ```bash
    make
    ```

2.  **Load the Module:**
    ```bash
    sudo insmod ai_agent.ko
    ```
    *Check logs:* `dmesg | tail` should show "AI_AGENT: Initializing LKM Agent..."

3.  **Compile the Client:**
    ```bash
    gcc user_client.c -o client
    ```

4.  **Talk to the Agent:**
    ```bash
    sudo ./client
    ```
    *Commands:*
    - `PREDICT 10` (Asks kernel to predict output for input 10)
    - `UPDATE 2 5` (Updates weights: Weight=2, Bias=5)

5.  **Check Inference Results:**
    Since the logic runs in kernel space, the results are logged to the kernel ring buffer:
    ```bash
    dmesg | tail
    ```

6.  **Unload:**
    ```bash
    sudo rmmod ai_agent
    make clean
    ```

## Security & Sandboxing
Running code in the kernel carries risks. We implement **Module Signing** to ensure integrity.

1.  **Sign the Module:**
    ```bash
    make sign
    ```
    This generates keys and cryptographically signs `ai_agent.ko`.

2.  **Read the Full Security Guide:**
    See [SECURITY.md](SECURITY.md) for details on:
    - Enforcing signature verification (`module.sig_enforce=1`)
    - Secure Boot Key Enrollment
    - Conceptual eBPF Sandboxing strategies

## Why Kernel Space?
- **Zero Latency:** No context switches for processing high-frequency sensor data interrupts.
- **Security:** Model weights are in kernel memory, harder for user-space malware to tamper with.
- **Integration:** Can directly control hardware actuators based on AI decisions.
