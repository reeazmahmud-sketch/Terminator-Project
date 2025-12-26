#!/usr/bin/env zsh
# ============================================================================
# 15-terminal-voice.zsh
# Voice integration for terminal - speak and listen
# ============================================================================

# Voice configuration
typeset -g VOICE_ENABLED=false
typeset -g VOICE_INPUT_LANG="en-US"
typeset -g VOICE_OUTPUT_LANG="en"
typeset -g VOICE_TEMP_DIR="${HOME}/.zsh_voice_temp"
typeset -g VOICE_PYTHON_CMD="python3"

# Check if voice dependencies are available
function _check_voice_deps() {
    if ! command -v "$VOICE_PYTHON_CMD" &> /dev/null; then
        echo "❌ Python3 not found. Voice features disabled."
        return 1
    fi
    
    # Check for speech recognition module
    if ! $VOICE_PYTHON_CMD -c "import speech_recognition" 2>/dev/null; then
        echo "⚠️  SpeechRecognition not installed. Run: pip3 install SpeechRecognition pyaudio"
        return 1
    fi
    
    # Check for TTS module
    if ! $VOICE_PYTHON_CMD -c "import gtts" 2>/dev/null; then
        echo "⚠️  gTTS not installed. Run: pip3 install gtts playsound"
        return 1
    fi
    
    return 0
}

# Initialize voice module
function _init_voice() {
    mkdir -p "$VOICE_TEMP_DIR"
    
    if _check_voice_deps; then
        VOICE_ENABLED=true
        echo "✅ Voice module initialized"
    else
        echo "ℹ️  Voice features disabled. Install dependencies to enable."
    fi
}

# Listen for voice input
function voice-listen() {
    if [[ "$VOICE_ENABLED" != "true" ]]; then
        echo "❌ Voice not enabled. Install dependencies first."
        return 1
    fi
    
    echo "🎤 Listening... (speak now)"
    
    local voice_script="$VOICE_TEMP_DIR/listen.py"
    cat > "$voice_script" << 'PYTHON_EOF'
import speech_recognition as sr
import sys

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            text = recognizer.recognize_google(audio)
            print(text)
            return 0
        except sr.WaitTimeoutError:
            print("ERROR: No speech detected", file=sys.stderr)
            return 1
        except sr.UnknownValueError:
            print("ERROR: Could not understand audio", file=sys.stderr)
            return 2
        except sr.RequestError as e:
            print(f"ERROR: Could not request results; {e}", file=sys.stderr)
            return 3
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 4

if __name__ == "__main__":
    sys.exit(listen())
PYTHON_EOF
    
    local result
    result=$($VOICE_PYTHON_CMD "$voice_script" 2>&1)
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        echo "📝 Heard: $result"
        echo "$result"
        return 0
    else
        echo "❌ $result"
        return $exit_code
    fi
}

# Speak text output
function voice-speak() {
    if [[ "$VOICE_ENABLED" != "true" ]]; then
        echo "❌ Voice not enabled. Install dependencies first."
        return 1
    fi
    
    local text="$*"
    if [[ -z "$text" ]]; then
        echo "Usage: voice-speak <text to speak>"
        return 1
    fi
    
    echo "🔊 Speaking: $text"
    
    local voice_script="$VOICE_TEMP_DIR/speak.py"
    cat > "$voice_script" << 'PYTHON_EOF'
from gtts import gTTS
import os
import sys
import tempfile

def speak(text, lang='en'):
    try:
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
            temp_file = fp.name
        
        # Generate speech
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_file)
        
        # Play audio (platform-specific)
        if sys.platform == 'darwin':  # macOS
            os.system(f'afplay "{temp_file}"')
        elif sys.platform == 'linux':
            os.system(f'mpg123 -q "{temp_file}" 2>/dev/null || aplay "{temp_file}" 2>/dev/null')
        elif sys.platform == 'win32':
            os.system(f'start /min "" "{temp_file}"')
        
        # Clean up
        os.unlink(temp_file)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit(speak(text))
PYTHON_EOF
    
    $VOICE_PYTHON_CMD "$voice_script" "$text"
}

# Voice command mode - listen and execute
function voice-command() {
    if [[ "$VOICE_ENABLED" != "true" ]]; then
        echo "❌ Voice not enabled. Install dependencies first."
        return 1
    fi
    
    echo "🎤 Voice Command Mode"
    echo "Say a command, and I'll execute it."
    echo "Say 'exit' or 'quit' to stop."
    echo ""
    
    while true; do
        local command=$(voice-listen)
        
        # Check for exit commands
        if [[ "$command" =~ ^(exit|quit|stop)$ ]]; then
            voice-speak "Exiting voice command mode"
            break
        fi
        
        if [[ -n "$command" ]]; then
            echo "➜ Executing: $command"
            voice-speak "Executing $command"
            
            # Execute the command
            eval "$command"
            local exit_code=$?
            
            if [[ $exit_code -eq 0 ]]; then
                voice-speak "Command completed successfully"
            else
                voice-speak "Command failed with error code $exit_code"
            fi
        fi
        
        echo ""
    done
}

# Voice chat with AI (integrates with ollama if available)
function voice-chat() {
    if [[ "$VOICE_ENABLED" != "true" ]]; then
        echo "❌ Voice not enabled. Install dependencies first."
        return 1
    fi
    
    if ! command -v ollama &> /dev/null; then
        echo "❌ Ollama not found. Install ollama for voice chat."
        return 1
    fi
    
    echo "💬 Voice Chat Mode (with AI)"
    echo "Speak your question, and AI will respond with voice."
    echo "Say 'exit', 'quit', or 'goodbye' to stop."
    echo ""
    
    while true; do
        local question=$(voice-listen)
        
        # Check for exit commands
        if [[ "$question" =~ ^(exit|quit|goodbye|stop)$ ]]; then
            voice-speak "Goodbye! Have a great day."
            break
        fi
        
        if [[ -n "$question" ]]; then
            echo "🤔 Thinking..."
            
            # Get AI response
            local response=$(ollama run llama3 "$question" 2>&1)
            
            echo "💭 AI: $response"
            echo ""
            
            # Speak the response
            voice-speak "$response"
        fi
        
        echo ""
    done
}

# ZLE widget to insert voice input at cursor
function _voice_input_widget() {
    echo ""
    local text=$(voice-listen)
    if [[ -n "$text" ]]; then
        BUFFER="${BUFFER}${text}"
        zle end-of-line
    fi
    zle reset-prompt
}

zle -N _voice_input_widget

# Key binding: Ctrl+V for voice input
bindkey '^V' _voice_input_widget

# Aliases
alias vl='voice-listen'
alias vs='voice-speak'
alias vc='voice-command'
alias vchat='voice-chat'

# Initialize
_init_voice

# Install script
function install-voice-deps() {
    echo "📦 Installing voice dependencies..."
    pip3 install --user SpeechRecognition pyaudio gtts playsound
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Dependencies installed. Restart terminal or run: source ~/.zshrc"
    else
        echo "❌ Installation failed. You may need to install portaudio first:"
        echo "   macOS: brew install portaudio"
        echo "   Linux: sudo apt-get install portaudio19-dev python3-pyaudio"
    fi
}

echo "✅ Terminal voice module loaded (Ctrl+V for voice input)"
[[ "$VOICE_ENABLED" == "true" ]] && echo "   Commands: vl (listen), vs (speak), vc (command mode), vchat (AI chat)"
