#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <algorithm>
#include <numeric>
#include <chrono>
#include <system_error>
#include <cassert>

// Error Handling: Custom error category
enum class CoreError {
    Success = 0,
    InvalidInput,
    ComputationFailure,
    MemoryAllocationError
};

class CoreErrorCategory : public std::error_category {
public:
    const char* name() const noexcept override {
        return "TerminatorCore";
    }

    std::string message(int ev) const override {
        switch (static_cast<CoreError>(ev)) {
            case CoreError::Success: return "Success";
            case CoreError::InvalidInput: return "Invalid input provided";
            case CoreError::ComputationFailure: return "Computation failed";
            case CoreError::MemoryAllocationError: return "Memory allocation failed";
            default: return "Unknown error";
        }
    }
};

const CoreErrorCategory& core_category() {
    static CoreErrorCategory instance;
    return instance;
}

std::error_code make_error_code(CoreError e) {
    return {static_cast<int>(e), core_category()};
}

namespace std {
    template <>
    struct is_error_code_enum<CoreError> : true_type {};
}

// Memory Management: RAII Wrapper for a Resource (Example)
class Resource {
public:
    Resource(const std::string& name) : name_(name) {
        // Simulating resource acquisition
        // std::cout << "Resource '" << name_ << "' acquired.\n";
    }
    ~Resource() {
        // Simulating resource release
        // std::cout << "Resource '" << name_ << "' released.\n";
    }
    
    // Disable copy to enforce unique ownership semantics where appropriate,
    // or rely on smart pointers.
    Resource(const Resource&) = delete;
    Resource& operator=(const Resource&) = delete;

    void process() const {
        // Work with resource
    }

private:
    std::string name_;
};

// Core Compute Module
class TerminatorCore {
public:
    TerminatorCore() {
        // Pre-allocate or initialize pools if needed
    }

    // [[nodiscard]] forces the caller to handle the return value (error code)
    [[nodiscard]] std::error_code perform_heavy_computation(int intensity, double& result_out) {
        if (intensity <= 0) {
            return CoreError::InvalidInput;
        }

        try {
            // Memory Management: Smart pointers
            auto resource = std::make_unique<Resource>("ComputeMatrix");
            resource->process();

            // Performance: std::vector with reserved capacity (avoid reallocs)
            std::vector<double> data;
            data.reserve(intensity);

            // Populate data
            for (int i = 0; i < intensity; ++i) {
                data.push_back(static_cast<double>(i) * 1.5);
            }

            // unsafe math optimization (-ffast-math allows reordering)
            double sum = std::accumulate(data.begin(), data.end(), 0.0);
            
            result_out = sum / intensity;
            
            return CoreError::Success;

        } catch (const std::bad_alloc&) {
            return CoreError::MemoryAllocationError;
        } catch (...) {
            return CoreError::ComputationFailure;
        }
    }
};

int main(int argc, char* argv[]) {
    // Quick CLI entry point for testing/invocation
    
    // Performance Metric: Latency
    auto start = std::chrono::high_resolution_clock::now();

    TerminatorCore core;
    double result = 0.0;
    int intensity = 1000000;

    if (argc > 1) {
        try {
            intensity = std::stoi(argv[1]);
        } catch (...) {
            std::cerr << "Invalid argument, using default intensity.\n";
        }
    }

    std::error_code ec = core.perform_heavy_computation(intensity, result);

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> latency = end - start;

    if (ec) {
        std::cerr << "Error: " << ec.message() << " (" << ec.value() << ")\n";
        return 1;
    }

    // Output JSON for Python parsing
    std::cout << "{\n";
    std::cout << "  \"status\": \"success\",\n";
    std::cout << "  \"result\": " << result << ",\n";
    std::cout << "  \"latency_ms\": " << latency.count() << ",\n";
    std::cout << "  \"intensity\": " << intensity << "\n";
    std::cout << "}\n";

    return 0;
}
