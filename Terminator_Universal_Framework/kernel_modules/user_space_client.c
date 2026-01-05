/*
 * Terminator Universal Framework
 * Architect: Reeaz Mahmud | AI Partner: Gemini
 * Date: December 17, 2025
 */

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
#include <time.h>

#include "ai_agent_ioctl.h"

#define DEVICE_PATH "/dev/ai_agent"

// Helper to get time in ns
long get_nanos() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long)ts.tv_sec * 1000000000L + ts.tv_nsec;
}

int main() {
    int fd;
    struct ai_request req;
    char input[256];
    int val1, val2;
    long start_t, end_t;

    printf("🚀 Connecting to High-Performance AI Kernel Agent...\n");
    fd = open(DEVICE_PATH, O_RDWR);
    if (fd < 0) {
        perror("Failed to open device");
        return 1;
    }
    printf("✅ Connected to %s\n\n", DEVICE_PATH);
    printf("Commands:\n");
    printf("  PREDICT <int>      : Run inference\n");
    printf("  UPDATE <w> <b>     : Update weights (Requires Root)\n");
    printf("  BENCH <count>      : Run performance benchmark\n");
    printf("  quit               : Exit\n\n");

    while (1) {
        printf("> ");
        if (fgets(input, sizeof(input), stdin) == NULL) break;
        input[strcspn(input, "\n")] = 0;

        if (strcmp(input, "quit") == 0) break;

        if (sscanf(input, "PREDICT %d", &val1) == 1) {
            req.op_code = 0;
            req.input_val = val1;
            
            start_t = get_nanos();
            if (ioctl(fd, AI_IOC_PREDICT, &req) == -1) {
                perror("Ioctl failed");
            } else {
                end_t = get_nanos();
                printf("💡 Output: %d (Latency: %ld ns kernel-side + syscall overhead)\n", 
                       req.input_val, end_t - start_t);
            }
        }
        else if (sscanf(input, "UPDATE %d %d", &val1, &val2) == 2) {
            req.op_code = 1;
            req.input_val = val1; // Weight
            req.param2 = val2;    // Bias
            
            if (ioctl(fd, AI_IOC_UPDATE, &req) == -1) {
                perror("Update failed (Are you root?)");
            } else {
                printf("✅ Model updated.\n");
            }
        }
        else if (sscanf(input, "BENCH %d", &val1) == 1) {
            printf("🏎️  Running %d predictions...\n", val1);
            req.op_code = 0;
            req.input_val = 10;
            
            start_t = get_nanos();
            for(int i=0; i<val1; i++) {
                ioctl(fd, AI_IOC_PREDICT, &req);
            }
            end_t = get_nanos();
            
            double avg_ns = (double)(end_t - start_t) / val1;
            printf("📊 Result: %.2f ns per inference (%.2f Million OPS)\n", 
                   avg_ns, 1000.0/avg_ns);
        }
        else {
            printf("Unknown command.\n");
        }
    }

    close(fd);
    return 0;
}