#ifndef AI_AGENT_IOCTL_H
#define AI_AGENT_IOCTL_H

#include <linux/ioctl.h>

// Define Magic Number for our driver
#define AI_IOC_MAGIC 'k'

// Data structures for ioctl
struct ai_request {
    int op_code;       // 0=Predict, 1=Update
    int input_val;     // Input for prediction or weight for update
    int param2;        // Bias for update (unused for predict)
};

struct ai_response {
    int result;        // Prediction result
    int status;        // 0=Success, <0=Error
    long processing_time_ns; // Nanoseconds taken
};

// Define IOCTL commands
// _IOWR(magic, seq, type) - Read/Write data
#define AI_IOC_PREDICT _IOWR(AI_IOC_MAGIC, 1, struct ai_request)
#define AI_IOC_UPDATE  _IOWR(AI_IOC_MAGIC, 2, struct ai_request)
#define AI_IOC_GET_CONFIG _IOR(AI_IOC_MAGIC, 3, struct ai_request)

#endif
