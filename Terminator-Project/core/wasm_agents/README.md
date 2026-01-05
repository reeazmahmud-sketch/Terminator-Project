# WebAssembly (Wasm) Agents

This directory contains source code for High-Performance Agents written in Rust and compiled to WebAssembly.

## Prerequisites
1.  **Install Rust:** `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
2.  **Add Wasm Target:** `rustup target add wasm32-unknown-unknown`

## Compilation
To compile the `calculator_agent`:

```bash
cd calculator_agent
rustc src/lib.rs --target wasm32-unknown-unknown --crate-type cdylib -O -o ../calculator_agent.wasm
```

## Usage in Terminator
The `WasmAgent` class in `core/wasm_agent_framework.py` can load this `.wasm` file.

```python
agent = WasmAgent("CalcBot", "core/wasm_agents/calculator_agent.wasm")
await agent.start()
```
