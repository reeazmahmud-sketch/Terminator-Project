<!--
  Terminator Universal Framework
  Architect: Reeaz Mahmud | AI Partner: Gemini
  Date: December 17, 2025
-->

# AI Kernel Agent Security & Sandboxing

Running AI logic in kernel space requires strict security measures. This document outlines the sandboxing strategy for the `ai_agent` LKM.

## 1. Module Signing (Integrity)

To prevent unauthorized or tampered AI models from loading into the kernel, we use **Cryptographic Module Signing**.

### Setup
1.  **Generate Keys:**
    The `sign_module.sh` script generates a dedicated keypair (`signing_key.pem`, `signing_key.x509`) for this agent.
    ```bash
    make sign
    ```

2.  **Enforce Verification:**
    On the target Linux machine, ensure the kernel enforces module signatures.
    Add `module.sig_enforce=1` to your kernel boot parameters (GRUB).
    ```bash
    cat /sys/module/module/parameters/sig_enforce
    # Should return 'Y'
    ```

3.  **Enroll Key (Secure Boot):**
    If Secure Boot is enabled, you must enroll the generated public key (`keys/signing_key.x509`) into the system's MOK (Machine Owner Key) list using `mokutil`.
    ```bash
    sudo mokutil --import keys/signing_key.x509
    ```

## 2. eBPF Sandboxing (Runtime Isolation)

While Module Signing ensures *integrity* (code hasn't changed), eBPF ensures *behavioral safety* (code doesn't do bad things).

### Strategy
We can attach an eBPF program to the `ai_agent`'s functions to monitor and restrict its actions.

#### Conceptual eBPF Hook (pseudo-code)
```c
// sandbox.bpf.c
SEC("kprobe/ai_predict")
int BPF_KPROBE(trace_predict, int input_val) {
    // 1. Audit: Log every prediction request
    bpf_printk("AI_AUDIT: Prediction requested for input %d", input_val);

    // 2. Policy: Deny inputs > 1000 (Example restriction)
    if (input_val > 1000) {
        bpf_printk("AI_BLOCK: Input too large!");
        // Note: kprobes are usually observing. For blocking, use LSM hooks.
        return -1; 
    }
    return 0;
}
```

### LSM Hooks (Linux Security Modules)
For strict enforcement, write a BPF LSM hook attached to `file_permission` or similar to restrict which processes can open `/dev/ai_agent`.

## 3. Memory Isolation (MPK)
The C code should ideally use **Memory Protection Keys (MPK)** (if supported by CPU/Kernel) to isolate the model weights buffer, making it read-only to the rest of the kernel.

*Currently:* The agent uses standard `kmalloc`.
*Upgrade:* Use `pkey_alloc` and `pkey_mprotect` in `ai_agent.c` for critical data structures.

## 4. Operational Security
- **Unload on Idle:** Use `rmmod` to remove the AI capability when not actively processing data.
- **Auditing:** Monitor `dmesg` for "AI_AGENT" logs.
