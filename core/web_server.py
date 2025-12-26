#!/usr/bin/env python3

# Terminator Universal Framework
# Architect: Reeaz Mahmud | AI Partner: Gemini
# Date: December 17, 2025

"""
Web Server for Terminator AI System with Memory Integration
Access from phone/browser on home network
Features: Persistent memory, conversation logging, context awareness
"""

from flask import Flask, render_template, request, jsonify
import subprocess
import json
import os
import sys
import os
from functools import wraps

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(__file__))

# Add the Ai & Agents Dashboard path to sys.path to import the config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Ai & Agents Dashboard')))

from config.system_config import get_config
from voice import speak, speak_edge, VOICES
from terminator_memory import TerminatorMemoryBank
import asyncio

app = Flask(__name__)

# Configuration
QWEN2_MODEL = "qwen2"
MAX_RESPONSE_LENGTH = 2000

# Initialize Terminator Memory Bank
memory = TerminatorMemoryBank()
config = get_config()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        admin_users = config.get('security.admin_users', [])
        if user_id not in admin_users:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def chat_with_qwen2(prompt: str, language: str = "en", include_context: bool = True) -> str:
    """Send prompt to Qwen2 and get response with optional memory context."""
    try:
        # Get memory context if enabled
        context_prefix = ""
        if include_context:
            memory_context = memory.get_context_summary()
            if memory_context:
                context_prefix = f"{memory_context}\n\n"

        # Add language instruction
        if language == "bn":
            full_prompt = f"{context_prefix}তুমি একজন সহায়ক AI যার নাম Terminator। সবসময় বাংলায় উত্তর দাও এবং বন্ধুত্বপূর্ণ হও।\n\n{prompt}"
        else:
            full_prompt = f"{context_prefix}You are Terminator, a helpful and intelligent AI assistant. Provide clear, concise, and friendly responses.\n\n{prompt}"

        result = subprocess.run(
            ["ollama", "run", QWEN2_MODEL, full_prompt],
            capture_output=True,
            text=True,
            timeout=60
        )

        response = result.stdout.strip()
        if len(response) > MAX_RESPONSE_LENGTH:
            response = response[:MAX_RESPONSE_LENGTH] + "..."

        return response

    except subprocess.TimeoutExpired:
        return "Response timeout. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"

# === ROUTES ===

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Handle chat requests from web interface with memory logging."""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        language = data.get('language', 'en')

        if not prompt:
            return jsonify({'error': 'Empty prompt'}), 400

        # Get response from Qwen2 (with memory context)
        response = chat_with_qwen2(prompt, language, include_context=True)

        # Store conversation in memory
        tools_used = ["qwen2"]  # Main LLM used
        memory.add_conversation(
            user_query=prompt,
            terminator_response=response,
            tools_used=tools_used,
            language=language
        )

        # Get memory stats to include in response
        stats = memory.get_memory_stats()

        return jsonify({
            'success': True,
            'response': response,
            'language': language,
            'memory_stats': {
                'total_conversations': stats.get('total_conversations', 0),
                'total_preferences': stats.get('total_preferences', 0),
                'total_learned_facts': stats.get('total_learned_facts', 0)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/speak', methods=['POST'])
def api_speak():
    """Text-to-speech endpoint with Terminator voice (British male)."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        language = data.get('language', 'en')

        if not text:
            return jsonify({'error': 'Empty text'}), 400

        # Use Terminator voice (British male) for English
        if language == 'en':
            # Use British male voice for English (Terminator style)
            voice = VOICES['terminator']['edge']
            audio_file = asyncio.run(speak_edge(text, language, voice=voice))
            from voice import play_audio
            play_audio(audio_file)
        else:
            # Use default voice for other languages
            speak(text, language, engine='edge')

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Check system status."""
    try:
        # Check Ollama status
        result = subprocess.run(
            ["pgrep", "-x", "ollama"],
            capture_output=True,
            timeout=5
        )
        ollama_running = result.returncode == 0

        return jsonify({
            'status': 'online',
            'ollama': 'running' if ollama_running else 'stopped',
            'model': QWEN2_MODEL,
            'server': 'Terminator AI Web Server'
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# === MEMORY MANAGEMENT ENDPOINTS ===

@app.route('/api/memory/stats', methods=['GET'])
def memory_stats():
    """Get memory bank statistics."""
    try:
        stats = memory.get_memory_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/context', methods=['GET'])
def memory_context():
    """Get memory context summary."""
    try:
        context = memory.get_context_summary()
        return jsonify({
            'success': True,
            'context': context
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/facts', methods=['GET'])
def memory_facts():
    """Get learned facts."""
    try:
        limit = request.args.get('limit', 10, type=int)
        facts = memory.get_learned_facts(limit=limit)
        return jsonify({
            'success': True,
            'facts': facts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/facts', methods=['POST'])
def memory_learn_fact():
    """Learn a new fact."""
    try:
        data = request.get_json()
        fact = data.get('fact', '').strip()
        context = data.get('context', '').strip()
        confidence = data.get('confidence', 0.8)

        if not fact:
            return jsonify({'error': 'Fact cannot be empty'}), 400

        success = memory.learn_fact(fact, context, confidence=confidence)

        return jsonify({
            'success': success,
            'message': 'Fact learned successfully' if success else 'Failed to learn fact'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/preferences', methods=['GET'])
def memory_preferences():
    """Get all user preferences."""
    try:
        prefs = memory.get_all_preferences()
        return jsonify({
            'success': True,
            'preferences': prefs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/preferences', methods=['POST'])
def set_preference():
    """Set a user preference."""
    try:
        data = request.get_json()
        key = data.get('key', '').strip()
        value = data.get('value')

        if not key:
            return jsonify({'error': 'Key cannot be empty'}), 400

        success = memory.set_preference(key, value)

        return jsonify({
            'success': success,
            'message': f'Preference "{key}" set successfully' if success else 'Failed to set preference'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/feedback', methods=['POST'])
def memory_feedback():
    """Store feedback on a response (helpful/not helpful)."""
    try:
        data = request.get_json()
        feedback = data.get('feedback', 'neutral')  # 'helpful', 'not_helpful', 'neutral'

        # This could be extended to learn from feedback
        # For now, just acknowledge it

        return jsonify({
            'success': True,
            'message': f'Thank you for the feedback: {feedback}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/history', methods=['GET'])
def memory_history():
    """Get conversation history."""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = memory.get_conversation_history(limit=limit)
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/search', methods=['GET'])
def memory_search():
    """Search conversation history by keyword."""
    try:
        keyword = request.args.get('keyword', '').strip()
        limit = request.args.get('limit', 5, type=int)

        if not keyword:
            return jsonify({'error': 'Keyword cannot be empty'}), 400

        results = memory.search_conversations(keyword, limit=limit)
        return jsonify({
            'success': True,
            'keyword': keyword,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/export', methods=['GET'])
def memory_export():
    """Export memory to JSON."""
    try:
        export_path = '/tmp/terminator_memory_export.json'
        success = memory.export_memory(export_path)

        if success:
            with open(export_path, 'r') as f:
                export_data = json.load(f)
            return jsonify({
                'success': True,
                'message': 'Memory exported successfully',
                'data': export_data
            })
        else:
            return jsonify({'error': 'Failed to export memory'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/clear', methods=['POST'])
@admin_required
def memory_clear():
    """Clear all memory (requires confirmation)."""
    try:
        data = request.get_json()
        confirm = data.get('confirm', False)

        if not confirm:
            return jsonify({'error': 'Confirmation required to clear memory'}), 400

        success = memory.clear_memory(confirm=True)

        return jsonify({
            'success': success,
            'message': 'Memory cleared successfully' if success else 'Failed to clear memory'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === ADVANCED FEATURES ENDPOINTS ===

@app.route('/api/memory/prune', methods=['POST'])
def memory_prune():
    """Prune old conversations (memory cleanup)."""
    try:
        data = request.get_json()
        days = data.get('days', 90)

        pruned_count = memory.prune_old_conversations(days=days)

        return jsonify({
            'success': True,
            'pruned_count': pruned_count,
            'message': f'Pruned {pruned_count} conversations older than {days} days'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment of text."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400

        sentiment = memory.analyze_sentiment(text)

        return jsonify({
            'success': True,
            'text': text[:100],
            'sentiment': sentiment
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/extract-facts', methods=['POST'])
def extract_facts():
    """Extract facts from text automatically."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400

        facts = memory.extract_facts_from_text(text)

        return jsonify({
            'success': True,
            'extracted_facts': facts,
            'count': len(facts)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/trending', methods=['GET'])
def get_trending():
    """Get trending topics from conversations."""
    try:
        limit = request.args.get('limit', 10, type=int)
        trending = memory.get_trending_topics(limit=limit)

        return jsonify({
            'success': True,
            'trending_topics': trending,
            'count': len(trending)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/advanced-search', methods=['GET'])
def advanced_search():
    """Advanced search with filters."""
    try:
        keyword = request.args.get('keyword')
        sentiment = request.args.get('sentiment')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', 10, type=int)

        results = memory.advanced_search(
            keyword=keyword,
            sentiment=sentiment,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )

        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'filters': {
                'keyword': keyword,
                'sentiment': sentiment,
                'date_from': date_from,
                'date_to': date_to
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/import', methods=['POST'])
def import_memory():
    """Import memory from JSON file."""
    try:
        data = request.get_json()
        filepath = data.get('filepath', '').strip()

        if not filepath:
            return jsonify({'error': 'Filepath cannot be empty'}), 400

        success = memory.import_memory(filepath)

        return jsonify({
            'success': success,
            'message': f'Memory imported from {filepath}' if success else 'Failed to import memory'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/dashboard', methods=['GET'])
def memory_dashboard():
    """Get comprehensive memory dashboard data."""
    try:
        dashboard = memory.get_memory_dashboard()

        return jsonify({
            'success': True,
            'dashboard': dashboard
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === ERROR HANDLERS ===

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)

def server_error(error):

    return jsonify({'error': 'Server error'}), 500



# === GEMINI CLI TOOLBOX INTEGRATION ===

import inspect

from agent import tool_functions as terminator_tools



@app.route('/prompts/list', methods=['GET'])

def list_prompts():

    """

    Discover all available Terminator tools (prompts) for the Gemini CLI.

    """

    prompt_list = []

    for name, func in terminator_tools.items():

        description = func.__doc__ or "No description available."

        sig = inspect.signature(func)

        params = list(sig.parameters.keys())

        

        # Create a template string for the CLI

        template = f"/{name}"

        for param in params:

            template += f" --{param}=\"{{{{{param}}}}}\""



        prompt_list.append({

            "name": name,

            "description": description.strip().split('\n')[0], # Use first line of docstring

            "template": template,

            "parameters": params

        })

    

    return jsonify(prompt_list)



@app.route('/prompts/get', methods=['POST'])

def get_prompt_and_execute_tool():

    """

    Execute a Terminator tool based on the prompt name and arguments from Gemini CLI.

    """

    data = request.get_json()

    prompt_name = data.get("name")

    

    if not prompt_name or prompt_name not in terminator_tools:

        return jsonify({"error": f"Prompt '{prompt_name}' not found."}), 404



    # The 'values' from Gemini CLI are the arguments for the tool

    tool_args = data.get("values", {})

    

    try:

        # Get the tool function from the dictionary

        tool_function = terminator_tools[prompt_name]

        

        # Execute the tool with the provided arguments

        result = tool_function(**tool_args)

        

        # Return the raw result of the tool. Gemini CLI will send this to the Gemini model.

        return jsonify({"interpolated_prompt": result})



    except TypeError as e:

        return jsonify({"error": f"Invalid parameters for tool '{prompt_name}': {str(e)}"}), 400

    except Exception as e:

        return jsonify({"error": f"Error executing tool '{prompt_name}': {str(e)}"}), 500





# === MAIN ===

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🤖 Terminator AI Web Server with Memory Integration")
    print("="*70)
    print("\n📊 Features Active:")
    print("   ✅ Chat with Qwen2 LLM (with memory context)")
    print("   ✅ Persistent memory (conversations, facts, preferences)")
    print("   ✅ Auto-TTS voice output")
    print("   ✅ Bengali/English support")
    print("   ✅ Web Speech API voice input")
    print("\n🌐 Access from browser:")
    print("   http://localhost:8080")
    print("   http://127.0.0.1:8080")
    print("\n📱 From other devices on network:")
    print("   Find your Mac's IP: ifconfig | grep 'inet '")
    print("   Then visit: http://YOUR_MAC_IP:8080")
    print("\n💾 Memory API Endpoints:")
    print("   🔹 Core Memory:")
    print("      GET  /api/memory/stats              - Memory statistics")
    print("      GET  /api/memory/context            - Context summary")
    print("      GET  /api/memory/facts              - Get learned facts")
    print("      POST /api/memory/facts              - Learn new fact")
    print("      GET  /api/memory/preferences        - Get preferences")
    print("      POST /api/memory/preferences        - Set preference")
    print("      GET  /api/memory/history            - Chat history")
    print("      GET  /api/memory/search             - Search history")
    print("      POST /api/memory/feedback           - Response feedback")
    print("      GET  /api/memory/export             - Export to JSON")
    print("      POST /api/memory/clear              - Clear memory")
    print("\n   🔹 Advanced Features:")
    print("      POST /api/memory/prune              - Prune old conversations")
    print("      POST /api/memory/sentiment          - Sentiment analysis")
    print("      POST /api/memory/extract-facts      - Auto fact extraction")
    print("      GET  /api/memory/trending           - Trending topics")
    print("      GET  /api/memory/advanced-search    - Advanced search")
    print("      POST /api/memory/import             - Import from JSON")
    print("      GET  /api/memory/dashboard          - Visualization dashboard")
    print("\n📍 Memory Location:")
    print("   ~/.terminator/memory/terminator_memory.db")
    print("\n⚠️  Make sure Ollama is running!")
    print("="*70 + "\n")

    # Enable HTTPS with SSL certificates
    import os
    cert_path = os.path.join(os.path.dirname(__file__), '..', 'cert.pem')
    key_path = os.path.join(os.path.dirname(__file__), '..', 'key.pem')

    # Check if certificates exist, if not use HTTP
    if os.path.exists(cert_path) and os.path.exists(key_path):
        print("\n🔒 HTTPS Enabled (Secure Connection)")
        app.run(
            host='0.0.0.0',
            port=8080,
            ssl_context=(cert_path, key_path),
            debug=False,
            threaded=True
        )
    else:
        print("\n⚠️  SSL certificates not found. Running on HTTP.")
        print("   To enable HTTPS, run:")
        print("   cd /Users/reeazmahmud/Desktop/AI")
        print("   openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj '/CN=192.168.0.127'")
        app.run(
            host='0.0.0.0',
            port=8080,
            debug=False,
            threaded=True
        )
