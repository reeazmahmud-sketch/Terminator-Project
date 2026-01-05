# Makefile for Terminator C++ Core Module

# Compiler and Flags
CXX = g++
CXXFLAGS = -std=c++20 -O3 -march=native -flto -Wextra -Wall -pipe -fomit-frame-pointer -ffast-math
LDFLAGS = -lstdc++ # Link C++ standard library

# Directories
SRC_DIR = .
OBJ_DIR = obj
BIN_DIR = bin

# Target executable
TARGET = terminator_core

# Source files (adjust as needed)
SRCS = $(wildcard $(SRC_DIR)/*.cpp)

# Object files
OBJS = $(patsubst $(SRC_DIR)/%.cpp,$(OBJ_DIR)/%.o,$(SRCS))

# Default target
all: $(BIN_DIR)/$(TARGET)

# Linker rule for the executable
$(BIN_DIR)/$(TARGET): $(OBJS) | $(BIN_DIR)
	@echo "Linking $@..."
	$(CXX) $(LDFLAGS) $^ -o $@
	@echo "Build complete: $(BIN_DIR)/$(TARGET)"

# Compilation rule for C++ source files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp | $(OBJ_DIR)
	@echo "Compiling $<..."
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Directory creation rules
$(OBJ_DIR):
	@mkdir -p $(OBJ_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Clean rule
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(OBJ_DIR) $(BIN_DIR)
	@echo "Clean complete."

.PHONY: all clean
