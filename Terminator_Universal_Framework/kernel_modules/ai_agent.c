/*
 * Terminator Universal Framework
 * Architect: Reeaz Mahmud | AI Partner: Gemini
 * Date: December 17, 2025
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/mutex.h>
#include <linux/ioctl.h>

#define DEVICE_NAME "ai_agent"
#define CLASS_NAME "ai_class"
#define INPUT_SIZE 4  // Single neuron input
#define FIXED_POINT_SHIFT 14  // Q15 fixed-point

MODULE_LICENSE("GPL");
MODULE_AUTHOR("AI Agent");
MODULE_DESCRIPTION("Kernel-space AI inference agent");

// Simulated quantized weights (fixed-point Q15)
static int16_t weights[INPUT_SIZE] = {16384, 8192, -8192, 0};  // 1.0, 0.5, -0.5, 0.0
static int16_t bias = 8192;  // 0.5

// Ioctl commands
#define AI_LOAD_WEIGHTS _IOW('A', 1, int16_t*)
#define AI_INFERENCE _IOR('A', 2, int16_t)

static int major_number;
static struct class* ai_class = NULL;
static struct device* ai_device = NULL;
static DEFINE_MUTEX(ai_mutex);

static int ai_open(struct inode *inodep, struct file *filep) {
    if (!mutex_trylock(&ai_mutex)) return -EBUSY;
    pr_info("AI Agent: opened\n");
    return 0;
}

static int ai_release(struct inode *inodep, struct file *filep) {
    mutex_unlock(&ai_mutex);
    pr_info("AI Agent: released\n");
    return 0;
}

// Fixed-point inference: sum(inputs[i] * weights[i]) >> SHIFT + bias
static ssize_t ai_write(struct file *filep, const char __user *buffer, size_t len, loff_t *offset) {
    int16_t inputs[INPUT_SIZE];
    int16_t output;
    int32_t sum;
    int i;

    if (len != INPUT_SIZE * sizeof(int16_t)) return -EINVAL;
    if (copy_from_user(inputs, buffer, len)) return -EFAULT;
    
    sum = bias;
    for (i = 0; i < INPUT_SIZE; i++) {
        sum += (int32_t)inputs[i] * weights[i];
    }
    output = (int16_t)(sum >> FIXED_POINT_SHIFT);
    
    // Note: The prompt code copies back to 'buffer' which is technically a write buffer (const char*)
    // Writing back to the input buffer in a .write op is unusual but possible if user passed a writable pointer.
    // However, usually we write to device, then read result.
    // The prompt explicitly says: "if (copy_to_user(buffer, &output, sizeof(output)))"
    // We will follow the prompt exactly, assuming the user space treats the buffer as in/out.
    // To allow this, we must cast away const.
    if (copy_to_user((void __user *)buffer, &output, sizeof(output))) return -EFAULT;
    
    pr_info("AI Agent: inference output=%d\n", output);
    return sizeof(output);
}

static long ai_ioctl(struct file *filep, unsigned int cmd, unsigned long arg) {
    switch (cmd) {
    case AI_LOAD_WEIGHTS:
        if (copy_from_user(weights, (int16_t*)arg, INPUT_SIZE * sizeof(int16_t)))
            return -EFAULT;
        pr_info("AI Agent: weights loaded\n");
        return 0;
    default:
        return -EINVAL;
    }
}

static struct file_operations fops = {
    .open = ai_open,
    .release = ai_release,
    .write = ai_write,
    .unlocked_ioctl = ai_ioctl,
};

static int __init ai_init(void) {
    pr_info("AI Agent: initializing\n");
    major_number = register_chrdev(0, DEVICE_NAME, &fops);
    if (major_number < 0) return major_number;
    
    ai_class = class_create(CLASS_NAME); 
    if (IS_ERR(ai_class)) {
        unregister_chrdev(major_number, DEVICE_NAME);
        return PTR_ERR(ai_class);
    }
    
    ai_device = device_create(ai_class, NULL, MKDEV(major_number, 0), NULL, DEVICE_NAME);
    if (IS_ERR(ai_device)) {
        class_destroy(ai_class);
        unregister_chrdev(major_number, DEVICE_NAME);
        return PTR_ERR(ai_device);
    }
    return 0;
}

static void __exit ai_exit(void) {
    device_destroy(ai_class, MKDEV(major_number, 0));
    class_destroy(ai_class);
    unregister_chrdev(major_number, DEVICE_NAME);
    pr_info("AI Agent: unloaded\n");
}

module_init(ai_init);
module_exit(ai_exit);
