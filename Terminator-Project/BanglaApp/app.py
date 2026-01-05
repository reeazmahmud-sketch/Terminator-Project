"""
Bangla Text Processor Web App
Created by: Claude
Purpose: Process Bangla/Bengali text with audio input, AI analysis, and suggestions
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
from PyPDF2 import PdfReader
from docx import Document
from werkzeug.utils import secure_filename
from deep_translator import GoogleTranslator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = '/tmp/bangla_uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md', 'rtf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path, filename):
    """Extract text from various file formats"""
    ext = filename.rsplit('.', 1)[1].lower()

    try:
        if ext == 'txt' or ext == 'md':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif ext == 'pdf':
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text

        elif ext == 'docx':
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text

        elif ext == 'rtf':
            # Basic RTF support - just read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

        else:
            return None

    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {e}")
        return None

# Bangla-Processor Agent
class BanglaProcessor:
    """Agent for processing Bengali/Bangla text"""

    def __init__(self):
        self.name = "Bangla-Processor"
        self.created_by = "Claude"

    def analyze_text(self, text):
        """Analyze Bangla text and provide feedback"""

        analysis = {
            "original_text": text,
            "word_count": len(text.split()),
            "character_count": len(text),
            "feedback": [],
            "suggestions": [],
            "beautified_text": text,
            "rating": 0,
            "opinion": ""
        }

        # Basic analysis
        if len(text) < 10:
            analysis["feedback"].append("⚠️ Text is very short. Consider adding more details.")
            analysis["rating"] = 3
        elif len(text) < 50:
            analysis["feedback"].append("✅ Good length for a short message.")
            analysis["rating"] = 7
        else:
            analysis["feedback"].append("✅ Excellent! Good amount of content.")
            analysis["rating"] = 9

        # Check for common patterns
        if "আমি" in text:
            analysis["suggestions"].append("💡 You're using first person ('আমি'). Consider if third person would be more formal.")

        if "।" not in text and len(text) > 20:
            analysis["suggestions"].append("💡 Add proper sentence endings with '।' (দাঁড়ি)")

        if text.isupper():
            analysis["suggestions"].append("💡 Using all caps. Consider using normal case for better readability.")
            analysis["beautified_text"] = text.title()

        # Spacing improvements
        if "  " in text:
            analysis["suggestions"].append("💡 Found extra spaces. Cleaned them up.")
            analysis["beautified_text"] = " ".join(text.split())

        # Generate opinion
        if analysis["rating"] >= 8:
            analysis["opinion"] = "🌟 Excellent! Your Bangla text is well-written and clear. The structure is good and the message comes through nicely."
        elif analysis["rating"] >= 6:
            analysis["opinion"] = "👍 Good work! Your text is readable and conveys the message. A few small improvements could make it even better."
        elif analysis["rating"] >= 4:
            analysis["opinion"] = "📝 Not bad! The text is understandable but could use some refinement. Consider the suggestions above."
        else:
            analysis["opinion"] = "💪 Keep practicing! Your text needs some work. Try adding more content and following Bangla grammar rules."

        return analysis

    def get_suggestions(self, text):
        """Get writing suggestions"""
        suggestions = []

        # Length-based suggestions
        if len(text) < 30:
            suggestions.append({
                "type": "length",
                "suggestion": "আপনার লেখা আরো বিস্তারিত করুন (Make your text more detailed)",
                "example": "যেমন: প্রসঙ্গ, উদাহরণ, বা ব্যাখ্যা যোগ করুন"
            })

        # Grammar suggestions
        suggestions.append({
            "type": "grammar",
            "suggestion": "বাক্যের শেষে দাঁড়ি (।) ব্যবহার করুন (Use '।' at sentence ends)",
            "example": "ভালো আছি। → ভালো আছি।"
        })

        # Style suggestions
        suggestions.append({
            "type": "style",
            "suggestion": "সুন্দর শব্দ চয়ন করুন (Choose beautiful words)",
            "example": "পানি → জল, খুব → অত্যন্ত"
        })

        return suggestions

# Initialize agent
bangla_agent = BanglaProcessor()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze Bangla text"""
    try:
        data = request.json
        text = data.get('text', '')

        if not text:
            return jsonify({"error": "No text provided"}), 400

        logger.info(f"Analyzing text: {text[:50]}...")

        # Analyze text
        result = bangla_agent.analyze_text(text)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/suggestions', methods=['POST'])
def suggestions():
    """Get writing suggestions"""
    try:
        data = request.json
        text = data.get('text', '')

        suggestions = bangla_agent.get_suggestions(text)

        return jsonify({"suggestions": suggestions})

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/beautify', methods=['POST'])
def beautify():
    """Beautify Bangla text"""
    try:
        data = request.json
        text = data.get('text', '')

        # Clean up text
        beautified = " ".join(text.split())  # Remove extra spaces
        beautified = beautified.strip()  # Remove leading/trailing spaces

        return jsonify({
            "original": text,
            "beautified": beautified,
            "changes": ["Removed extra spaces", "Trimmed whitespace"]
        })

    except Exception as e:
        logger.error(f"Error beautifying text: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/import-url', methods=['POST'])
def import_url():
    """Import text from URL (websites, social media)"""
    try:
        data = request.json
        url = data.get('url', '')

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        logger.info(f"Importing text from URL: {url}")

        # Simple URL text extraction (in production, use BeautifulSoup or newspaper3k)
        import urllib.request
        from html.parser import HTMLParser

        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []

            def handle_data(self, data):
                if data.strip():
                    self.text.append(data.strip())

        # Fetch the URL
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')

        # Extract text
        parser = TextExtractor()
        parser.feed(html)
        extracted_text = ' '.join(parser.text)

        if not extracted_text:
            return jsonify({"error": "Could not extract text from URL"}), 400

        return jsonify({
            "url": url,
            "text": extracted_text[:5000],  # Limit to 5000 chars
            "message": f"Successfully imported text from {url}"
        })

    except Exception as e:
        logger.error(f"Error importing from URL: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/check-inbox', methods=['GET'])
def check_inbox():
    """Check for email/SMS messages (demo - requires actual email/SMS API)"""
    try:
        # This is a placeholder for actual email/SMS integration
        # In production, you would use:
        # - Twilio API for SMS
        # - SendGrid/Mailgun for email
        # - Or connect to IMAP server

        # Demo response - simulating inbox check
        messages = []

        # For now, return demo message indicating setup needed
        return jsonify({
            "messages": messages,
            "message": "Email/SMS integration requires API setup (Twilio, SendGrid, etc.)",
            "setup_required": True
        })

    except Exception as e:
        logger.error(f"Error checking inbox: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    """Translate text to Bangla from English, Hindi, or Arabic"""
    try:
        data = request.json
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'en')
        target_lang = data.get('target_lang', 'bn')

        if not text:
            return jsonify({"error": "No text provided"}), 400

        logger.info(f"Translating from {source_lang} to {target_lang}: {text[:50]}...")

        # Language code mapping for GoogleTranslator
        lang_map = {
            'en': 'en',  # English
            'hi': 'hi',  # Hindi
            'ar': 'ar',  # Arabic
            'bn': 'bn'   # Bangla/Bengali
        }

        source_code = lang_map.get(source_lang, 'en')
        target_code = lang_map.get(target_lang, 'bn')

        # Translate using Google Translator
        translator = GoogleTranslator(source=source_code, target=target_code)
        translated_text = translator.translate(text)

        return jsonify({
            "source_lang": source_lang,
            "target_lang": target_lang,
            "source_text": text,
            "translated_text": translated_text,
            "message": f"Successfully translated from {source_lang} to {target_lang}"
        })

    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and extract text from file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        # Check if filename is empty
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                "error": f"File type not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400

        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        logger.info(f"File uploaded: {filename}")

        # Extract text from file
        extracted_text = extract_text_from_file(file_path, filename)

        # Clean up uploaded file
        os.remove(file_path)

        if extracted_text is None:
            return jsonify({"error": "Could not extract text from file"}), 500

        return jsonify({
            "filename": filename,
            "text": extracted_text,
            "message": f"Successfully extracted text from {filename}"
        })

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Bangla Text Processor Web App")
    logger.info(f"📍 Open: http://localhost:5002")
    app.run(debug=True, port=5002, host='0.0.0.0')
