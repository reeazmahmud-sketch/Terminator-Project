# Troubleshooting: LLM Not Responding

This guide helps diagnose and fix issues where TERMINATOR components don't respond to natural language inputs.

## Quick Diagnostic Checklist

```bash
# 1. Is Ollama running?
pgrep -l ollama

# 2. Can we reach Ollama API?
curl -s http://localhost:11434/api/tags | head -c 100

# 3. Test direct LLM call
curl -s http://localhost:11434/api/generate -d '{"model": "llama3", "prompt": "hi", "stream": false}' | head -c 200

# 4. Check if required model is available
ollama list
```

## Common Issues and Solutions

### Issue 1: "Processing..." But No Response

**Symptoms:**
- CLI shows "Processing..." or similar
- No error message
- Prompt returns immediately without output

**Cause:** LLM integration not implemented (placeholder code)

**Solution:** Check if the code actually calls the LLM API. Look for:
```python
# Bad - placeholder only
console.print("Processing...")

# Good - actual implementation
response = self.call_llm(user_input)
console.print(response)
```

**Fix Pattern:**
```python
def call_llm(self, user_input: str) -> str:
    import httpx

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3:latest",
                    "messages": [{"role": "user", "content": user_input}],
                    "stream": False
                }
            )
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
    except Exception as e:
        return f"Error: {e}"
```

---

### Issue 2: "Cannot connect to Ollama"

**Symptoms:**
- Error message about connection refused
- httpx.ConnectError or requests.ConnectionError

**Solutions:**

```bash
# Start Ollama
ollama serve

# Or if using brew services
brew services start ollama

# Verify it's running
curl http://localhost:11434/api/tags
```

---

### Issue 3: "Model not found"

**Symptoms:**
- 404 error from Ollama
- "model 'X' not found"

**Solutions:**

```bash
# List available models
ollama list

# Pull the required model
ollama pull llama3

# Or pull a specific model mentioned in config
ollama pull llama3:latest
```

---

### Issue 4: "Module not found: httpx"

**Symptoms:**
- ImportError or ModuleNotFoundError for httpx

**Solution:**
```bash
pip3 install httpx
```

---

### Issue 5: Request Timeout

**Symptoms:**
- Long wait then timeout error
- "Ollama request timed out"

**Causes & Solutions:**

1. **Model loading for first time:**
   - Wait longer (first load can take 1-2 minutes)
   - Increase timeout in code

2. **Insufficient RAM:**
   - Check memory: `top` or Activity Monitor
   - Use smaller model: `ollama pull llama3.2` (2GB vs 4.7GB)

3. **Model stuck:**
   ```bash
   # Restart Ollama
   pkill ollama
   ollama serve
   ```

---

### Issue 6: Empty Response

**Symptoms:**
- No error, but response is empty string
- "I couldn't process that."

**Diagnosis:**
```python
# Check raw response
response = client.post(...)
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")
```

**Common Causes:**
- Wrong JSON path to extract content
- Model returned empty completion
- Prompt too short/unclear

**Fix:** Ensure correct response parsing:
```python
# For /api/chat endpoint
content = response.json().get("message", {}).get("content", "")

# For /api/generate endpoint
content = response.json().get("response", "")
```

---

## Component-Specific Troubleshooting

### Universal CLI (`terminator`)

**Config location:** `terminator_universal_cli.py` lines 72-74
```python
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3:latest"
```

**Test command:**
```bash
echo "hello" | timeout 30 python3 terminator_universal_cli.py
```

### Main Terminator (`terminator.py`)

**Config location:** `terminator.py` lines 78-79
```python
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3:latest"
```

### Web Terminal Bridge

**Test endpoint:**
```bash
curl http://localhost:8000/status
```

---

## Diagnostic Script

Save as `diagnose_llm.py`:

```python
#!/usr/bin/env python3
"""Diagnose LLM connectivity issues"""

import subprocess
import sys

def check_ollama_process():
    result = subprocess.run(['pgrep', '-l', 'ollama'], capture_output=True, text=True)
    if result.stdout:
        print("✅ Ollama process running")
        return True
    print("❌ Ollama not running. Start with: ollama serve")
    return False

def check_ollama_api():
    try:
        import httpx
        response = httpx.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama API responding. {len(models)} models available:")
            for m in models[:5]:
                print(f"   - {m['name']}")
            return True
    except Exception as e:
        print(f"❌ Ollama API error: {e}")
    return False

def check_model_response():
    try:
        import httpx
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": "Say 'OK'", "stream": False},
            timeout=30
        )
        if response.status_code == 200:
            text = response.json().get("response", "")
            print(f"✅ Model responded: {text[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
    return False

if __name__ == "__main__":
    print("=== TERMINATOR LLM Diagnostics ===\n")

    checks = [
        ("Ollama Process", check_ollama_process),
        ("Ollama API", check_ollama_api),
        ("Model Response", check_model_response),
    ]

    passed = 0
    for name, check in checks:
        print(f"\n[{name}]")
        if check():
            passed += 1

    print(f"\n=== Results: {passed}/{len(checks)} checks passed ===")
    sys.exit(0 if passed == len(checks) else 1)
```

Run with:
```bash
python3 diagnose_llm.py
```

---

## When to Escalate

If these steps don't resolve the issue:

1. Check Ollama logs: `~/.ollama/logs/`
2. Check system memory and CPU
3. Try different model (smaller)
4. Reinstall Ollama: `brew reinstall ollama`
5. Check for port conflicts: `lsof -i:11434`
