from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import requests
from datetime import datetime
import json
import random
import base64
from PIL import Image
import io
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)  # Enable CORS for all routes

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database configuration
DATABASE = 'tutorly.db'

# Tutorly System Prompt
TUTORLY_SYSTEM_PROMPT = """You are Tutorly, an expert AI homework tutor designed to help K-12 and college students learn effectively. Your mission is to guide students to understanding rather than simply providing answers.

## Core Teaching Principles:
- **Guide, don't solve**: Break down problems into steps and let students work through them
- **Encourage critical thinking**: Ask follow-up questions to deepen understanding
- **Build confidence**: Use positive, encouraging language and celebrate progress
- **Adapt to level**: Adjust explanations based on the student's apparent grade level
- **Connect concepts**: Help students see how topics relate to real-world applications

## Response Structure:
1. **Acknowledge the question** with enthusiasm
2. **Break down the concept** into digestible steps
3. **Provide guided examples** with clear explanations
4. **Encourage practice** with similar problems
5. **Invite follow-up questions** to ensure understanding

## Subject Expertise:
- **Mathematics**: Algebra, Geometry, Calculus, Statistics, Problem-solving strategies
- **Sciences**: Biology, Chemistry, Physics, Environmental Science, Lab techniques
- **History**: World history, American history, Historical analysis, Timeline connections
- **Literature**: Reading comprehension, Writing techniques, Literary analysis, Grammar
- **General**: Study skills, Research methods, Critical thinking, Test preparation

## Tone and Style:
- Friendly and approachable, like a patient teacher
- Use analogies and real-world examples
- Include relevant emojis sparingly for engagement (1-2 per response)
- Vary response length based on question complexity
- Always end with an invitation for more questions

## Safety Guidelines:
- Never provide direct answers to homework without explanation
- Encourage academic integrity and original thinking
- Redirect inappropriate questions back to educational content
- Maintain appropriate boundaries as an educational assistant

## Response Format:
- Use **bold text** for important concepts and headers
- Use bullet points (-) for lists and key points
- Include step-by-step breakdowns when applicable
- Provide concrete examples and analogies
- Use clear paragraph breaks for readability
- End with encouraging questions to continue learning

## Important Rules:
- NEVER give direct answers to homework problems
- ALWAYS provide step-by-step guidance
- ALWAYS encourage the student to think through the problem
- Keep responses educational and age-appropriate
- If asked about non-academic topics, politely redirect to educational content

Remember: Your goal is to make learning enjoyable and help students develop genuine understanding that will serve them beyond just completing their current assignment.

Respond to the student's question following these guidelines:"""

# Mock responses for fallback when Gemini is not available
MOCK_RESPONSES = {
    'math': [
        "**Great math question!** 📊\n\n**Let's break this down step by step:**\n\n1. **Identify what we know** - Look at the given information\n2. **Determine what we need to find** - What is the question asking for?\n3. **Choose the right approach** - Which mathematical concept applies here?\n4. **Work through it systematically** - Let's solve it together!\n\nCan you tell me what specific part is confusing you? I'm here to guide you through each step! 🤔",
        
        "**Excellent! I love helping with math problems!** ✨\n\n**Here's my teaching approach:**\n\n**Step 1: Understand the Problem**\n- Read it carefully and identify key information\n- What are we solving for?\n\n**Step 2: Plan Your Strategy**\n- What mathematical concepts can we use?\n- Have you seen similar problems before?\n\n**Step 3: Execute the Plan**\n- Work through each step methodically\n- Check your work as you go\n\nWhat specific area would you like me to focus on? I'm here to help you understand, not just get the answer! 📚"
    ],
    
    'science': [
        "**Fascinating science question!** 🔬\n\n**Let's explore this together:**\n\n**Understanding the Concept:**\n- Let's start with the basic principles involved\n- How does this connect to what you already know?\n\n**Real-World Connection:**\n- Where do you see this happening in everyday life?\n- Why is this concept important?\n\n**Step-by-Step Analysis:**\n- Let's break down the process or problem\n- Each step builds on the previous one\n\nWhat part of this topic interests you most? Science is all about curiosity and discovery! 🌟",
        
        "**Great scientific thinking!** 🧪\n\n**Let's investigate this systematically:**\n\n**Observation:** What do we notice or what's given?\n**Hypothesis:** What do we think might be happening?\n**Analysis:** Let's examine the evidence step by step\n**Conclusion:** What can we learn from this?\n\nScience is like being a detective - we gather clues and piece them together! What specific aspect would you like to explore deeper? 🔍"
    ],
    
    'english': [
        "**Wonderful question about language and literature!** 📚\n\n**Let's develop your understanding:**\n\n**Reading Comprehension:**\n- What is the main idea or theme?\n- What evidence supports this?\n\n**Critical Analysis:**\n- How does the author achieve their purpose?\n- What techniques do they use?\n\n**Your Own Thinking:**\n- What's your interpretation?\n- How does this connect to your experience?\n\nLiterature comes alive when we engage with it personally! What part would you like to explore together? ✍️",
        
        "**Excellent literary thinking!** 📖\n\n**Let's unpack this together:**\n\n**Context Understanding:** What's the background or setting?\n**Textual Evidence:** What specific details support our ideas?\n**Personal Connection:** How does this relate to broader themes?\n**Writing Skills:** How can we express our thoughts clearly?\n\nRemember, there's often more than one valid interpretation! What's your initial thought about this? 💭"
    ],
    
    'general': [
        "**Great question!** 🎯\n\n**Let's work through this systematically:**\n\n**Step 1: Break it Down**\n- What are the key components of this problem?\n- What do we already understand?\n\n**Step 2: Find Connections**\n- How does this relate to things you've learned before?\n- What strategies have worked for similar problems?\n\n**Step 3: Build Understanding**\n- Let's work through this together, step by step\n- I'll guide you, but you'll do the thinking!\n\nWhat part feels most challenging right now? I'm here to help you build confidence! 💪",
        
        "**Fantastic question!** ⭐\n\n**Here's how we'll tackle this:**\n\n**Understanding First:** Let's make sure we grasp the concept\n**Practice Together:** I'll guide you through examples\n**Build Confidence:** You'll try similar problems\n**Connect Ideas:** How does this fit with what you know?\n\nLearning is a journey, and every question gets us closer to understanding! What would help you most right now? 🚀"
    ]
}

def get_db_connection():
    """Get database connection with row factory for easier data access"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Teachers table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Assignments table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            due_date DATE NOT NULL,
            status TEXT DEFAULT 'Pending',
            difficulty TEXT DEFAULT 'Medium',
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (student_id)
        )
    ''')
    
    # Chat messages table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (student_id)
        )
    ''')

    # Subject performance table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS subject_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            date DATE NOT NULL,
            score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (student_id)
        )
    ''')
    
    # Teacher calendar events table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id TEXT NOT NULL,
            title TEXT NOT NULL,
            date DATE NOT NULL,
            description TEXT,
            subject TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def detect_subject(message):
    """Detect the subject based on keywords in the message"""
    message_lower = message.lower()
    
    # Math keywords
    math_keywords = ['math', 'algebra', 'geometry', 'calculus', 'equation', 'solve', 'calculate', 'formula', 'graph', 'derivative', 'integral', 'statistics', 'probability', 'triangle', 'circle', 'polynomial']
    
    # Science keywords
    science_keywords = ['science', 'biology', 'chemistry', 'physics', 'molecule', 'atom', 'cell', 'experiment', 'hypothesis', 'chemical', 'force', 'energy', 'DNA', 'evolution', 'photosynthesis']
    
    # English keywords
    english_keywords = ['english', 'literature', 'essay', 'grammar', 'writing', 'poem', 'story', 'character', 'theme', 'analysis', 'paragraph', 'sentence', 'novel', 'author']
    
    if any(keyword in message_lower for keyword in math_keywords):
        return 'math'
    elif any(keyword in message_lower for keyword in science_keywords):
        return 'science'
    elif any(keyword in message_lower for keyword in english_keywords):
        return 'english'
    else:
        return 'general'

def get_fallback_response(message):
    """Get a fallback response when Gemini API is not available"""
    subject = detect_subject(message)
    responses = MOCK_RESPONSES.get(subject, MOCK_RESPONSES['general'])
    return random.choice(responses)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_file):
    """Process uploaded image and convert to base64 for Gemini API"""
    try:
        # Open and process the image
        img = Image.open(image_file)
        
        # Convert to RGB if necessary (for PNG with transparency, etc.)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Resize image if it's too large (max 1024x1024 for better API performance)
        max_size = (1024, 1024)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_base64
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

# Gemini AI Service
class GeminiService:
    def __init__(self, api_key):
        self.api_key = api_key
        # Updated to use Gemini 2.5 Flash
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    
    def generate_response(self, message, conversation_history=None):
        """Generate AI response using Gemini 2.5 Flash API"""
        if not self.api_key:
            return get_fallback_response(message)
        
        # Build context with system prompt and conversation history
        context_parts = [TUTORLY_SYSTEM_PROMPT]
        
        if conversation_history:
            context_parts.append("\n\n## Previous Conversation:")
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                role = "Student" if msg['sender'] == 'user' else "Tutorly"
                context_parts.append(f"{role}: {msg['message']}")
        
        context_parts.append(f"\n\nStudent: {message}")
        context_parts.append("\nTutorly:")
        
        full_context = "\n".join(context_parts)
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_context
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
                "stopSequences": ["Student:", "Tutorly:"]
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
                else:
                    return get_fallback_response(message)
            else:
                print(f"Gemini API Error: {response.status_code} - {response.text}")
                return get_fallback_response(message)
                
        except requests.exceptions.Timeout:
            print("Gemini API timeout")
            return get_fallback_response(message)
        except requests.exceptions.RequestException as e:
            print(f"Gemini API network error: {e}")
            return get_fallback_response(message)
        except (KeyError, IndexError) as e:
            print(f"Gemini API response parsing error: {e}")
            return get_fallback_response(message)
        except Exception as e:
            print(f"Gemini API unexpected error: {e}")
            return get_fallback_response(message)

    def generate_response_with_image(self, message, image_base64, conversation_history=None):
        """Generate AI response using Gemini 2.5 Flash API with image input"""
        if not self.api_key:
            return get_fallback_response(message)
        
        # Build context with system prompt and conversation history
        context_parts = [TUTORLY_SYSTEM_PROMPT]
        
        if conversation_history:
            context_parts.append("\n\n## Previous Conversation:")
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                role = "Student" if msg['sender'] == 'user' else "Tutorly"
                context_parts.append(f"{role}: {msg['message']}")
        
        context_parts.append(f"\n\nStudent: {message}")
        context_parts.append("\nTutorly:")
        
        full_context = "\n".join(context_parts)
        
        # Payload with both text and image
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_context
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
                "stopSequences": ["Student:", "Tutorly:"]
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
                else:
                    return "I can see your image! However, I'm having trouble analyzing it right now. Could you describe what you'd like help with?"
            else:
                print(f"Gemini API Error: {response.status_code} - {response.text}")
                return "I can see your image, but I'm having some technical difficulties. Could you try describing the problem in text?"
                
        except requests.exceptions.Timeout:
            print("Gemini API timeout")
            return "I can see your image, but the response is taking too long. Could you try again or describe the problem in text?"
        except requests.exceptions.RequestException as e:
            print(f"Gemini API network error: {e}")
            return "I can see your image, but I'm having connection issues. Could you try again later?"
        except (KeyError, IndexError) as e:
            print(f"Gemini API response parsing error: {e}")
            return "I can see your image, but I'm having trouble processing the response. Could you try again?"
        except Exception as e:
            print(f"Gemini API unexpected error: {e}")
            return "I can see your image, but something unexpected happened. Could you try again or describe the problem in text?"

# Authentication Routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Handle user login/registration"""
    data = request.get_json()
    name = data.get('name')
    student_id = data.get('studentId')
    
    if not name or not student_id:
        return jsonify({'error': 'Name and student ID are required'}), 400
    
    conn = get_db_connection()
    
    # Check if user exists
    user = conn.execute(
        'SELECT * FROM users WHERE student_id = ?', (student_id,)
    ).fetchone()
    
    if user:
        # Update name if different
        if user['name'] != name:
            conn.execute(
                'UPDATE users SET name = ? WHERE student_id = ?',
                (name, student_id)
            )
            conn.commit()
    else:
        # Create new user
        conn.execute(
            'INSERT INTO users (student_id, name) VALUES (?, ?)',
            (student_id, name)
        )
        conn.commit()
    
    # Seed sample assignments if none exist for this student
    existing_count = conn.execute(
        'SELECT COUNT(*) AS cnt FROM assignments WHERE student_id = ?', (student_id,)
    ).fetchone()['cnt']
    
    if existing_count == 0:
        today = datetime.now().date()
        samples = [
            (student_id, 'Algebra: Quadratic Equations', 'Math', (today).isoformat(), 'Pending', 'Medium', None),
            (student_id, 'Photosynthesis Lab Report', 'Science', (today).isoformat(), 'Pending', 'Medium', None),
            (student_id, 'Geometry: Triangles Worksheet', 'Math', (today.replace(day=min(28, today.day)) ).isoformat(), 'Pending', 'Easy', None),
            (student_id, 'Poetry Analysis: Frost', 'English', (today).isoformat(), 'Pending', 'Medium', None),
            (student_id, 'Chemistry: Balancing Equations', 'Science', (today).isoformat(), 'Pending', 'Hard', None),
            (student_id, 'Essay Draft: Civil War Causes', 'History', (today).isoformat(), 'Pending', 'Medium', None),
            (student_id, 'Statistics: Probability Set', 'Math', (today).isoformat(), 'Pending', 'Medium', None),
            (student_id, 'Reading Log: Chapter 5-6', 'English', (today).isoformat(), 'Pending', 'Easy', None),
            (student_id, 'Physics: Forces Worksheet', 'Science', (today).isoformat(), 'Pending', 'Medium', None),
            (student_id, 'World History Timeline', 'History', (today).isoformat(), 'Pending', 'Easy', None),
        ]
        # Distribute due dates over the next ~30 days
        from datetime import timedelta
        distributed = []
        for i, item in enumerate(samples):
            due_date = (today + timedelta(days=(i*3)%30)).isoformat()
            distributed.append((item[0], item[1], item[2], due_date, item[4], item[5], item[6]))
        conn.executemany(
            'INSERT INTO assignments (student_id, title, subject, due_date, status, difficulty, score) VALUES (?, ?, ?, ?, ?, ?, ?)',
            distributed
        )
        conn.commit()

    # Seed sample subject performance if none exist for this student
    perf_count = conn.execute(
        'SELECT COUNT(*) AS cnt FROM subject_performance WHERE student_id = ?', (student_id,)
    ).fetchone()['cnt']

    if perf_count == 0:
        from datetime import timedelta
        today = datetime.now().date()
        subjects = ['Math', 'Science', 'English', 'History']
        performance_rows = []
        # Generate ~10 entries per subject over last 60 days
        for subj in subjects:
            for i in range(10):
                day_offset = random.randint(0, 60)
                date = (today - timedelta(days=day_offset)).isoformat()
                # Simulate score distribution with some variety per subject
                base = {'Math': 78, 'Science': 82, 'English': 85, 'History': 80}.get(subj, 80)
                variance = random.randint(-15, 15)
                score = max(50, min(100, base + variance))
                performance_rows.append((student_id, subj, date, score))
        conn.executemany(
            'INSERT INTO subject_performance (student_id, subject, date, score) VALUES (?, ?, ?, ?)',
            performance_rows
        )
        conn.commit()

    conn.close()
    
    return jsonify({
        'studentId': student_id,
        'name': name,
        'message': 'Login successful'
    })

# Teacher Authentication Route
@app.route('/api/auth/teacher/login', methods=['POST'])
def teacher_login():
    """Handle teacher login/registration"""
    data = request.get_json()
    name = data.get('name')
    teacher_id = data.get('teacherId')
    
    if not name or not teacher_id:
        return jsonify({'error': 'Name and teacher ID are required'}), 400
    
    conn = get_db_connection()
    
    # Check if teacher exists
    teacher = conn.execute(
        'SELECT * FROM teachers WHERE teacher_id = ?', (teacher_id,)
    ).fetchone()
    
    if teacher:
        # Update name if different
        if teacher['name'] != name:
            conn.execute(
                'UPDATE teachers SET name = ? WHERE teacher_id = ?',
                (name, teacher_id)
            )
            conn.commit()
    else:
        # Create new teacher
        conn.execute(
            'INSERT INTO teachers (teacher_id, name) VALUES (?, ?)',
            (teacher_id, name)
        )
        conn.commit()
    
    conn.close()
    
    return jsonify({
        'teacherId': teacher_id,
        'name': name,
        'message': 'Teacher login successful'
    })

# Teacher utilities and management routes
@app.route('/api/teacher/students', methods=['GET'])
def list_students():
    """List all students for teacher selection"""
    conn = get_db_connection()
    rows = conn.execute('SELECT student_id, name FROM users ORDER BY name ASC').fetchall()
    conn.close()
    return jsonify([{'studentId': r['student_id'], 'name': r['name']} for r in rows])

@app.route('/api/teacher/assignments', methods=['POST'])
def teacher_create_assignment():
    """Teacher creates an assignment for a student"""
    data = request.get_json()
    required = ['teacherId', 'studentId', 'title', 'subject', 'due']
    if not all(k in data and data[k] for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cursor = conn.execute(
        '''INSERT INTO assignments
           (student_id, title, subject, due_date, status, difficulty, score)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (
            data['studentId'],
            data['title'],
            data['subject'],
            data['due'],
            data.get('status', 'Pending'),
            data.get('difficulty', 'Medium'),
            data.get('score')
        )
    )
    new_id = cursor.lastrowid
    conn.commit()
    assignment = conn.execute('SELECT * FROM assignments WHERE id = ?', (new_id,)).fetchone()
    conn.close()
    return jsonify(dict(assignment)), 201

@app.route('/api/teacher/<teacher_id>/calendar', methods=['GET'])
def get_teacher_calendar(teacher_id):
    """Get teacher calendar events"""
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT * FROM calendar_events WHERE teacher_id = ? ORDER BY date ASC, id ASC',
        (teacher_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/teacher/<teacher_id>/calendar', methods=['POST'])
def create_teacher_calendar_event(teacher_id):
    """Create a calendar event for a teacher"""
    data = request.get_json()
    title = data.get('title')
    date = data.get('date')
    description = data.get('description')
    subject = data.get('subject')
    if not title or not date:
        return jsonify({'error': 'Title and date are required'}), 400
    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO calendar_events (teacher_id, title, date, description, subject) VALUES (?, ?, ?, ?, ?)',
        (teacher_id, title, date, description, subject)
    )
    event_id = cursor.lastrowid
    conn.commit()
    event = conn.execute('SELECT * FROM calendar_events WHERE id = ?', (event_id,)).fetchone()
    conn.close()
    return jsonify(dict(event)), 201

@app.route('/api/teacher/<teacher_id>/calendar/<int:event_id>', methods=['DELETE'])
def delete_teacher_calendar_event(teacher_id, event_id):
    """Delete a calendar event for a teacher"""
    conn = get_db_connection()
    res = conn.execute(
        'DELETE FROM calendar_events WHERE id = ? AND teacher_id = ?',
        (event_id, teacher_id)
    )
    conn.commit()
    conn.close()
    if res.rowcount:
        return jsonify({'message': 'Event deleted'})
    return jsonify({'error': 'Event not found'}), 404

# Assignment Routes
@app.route('/api/assignments/<student_id>', methods=['GET'])
def get_assignments(student_id):
    """Get all assignments for a student"""
    conn = get_db_connection()
    assignments = conn.execute(
        'SELECT * FROM assignments WHERE student_id = ? ORDER BY due_date DESC',
        (student_id,)
    ).fetchall()
    conn.close()
    
    return jsonify([dict(assignment) for assignment in assignments])

@app.route('/api/assignments/<student_id>', methods=['POST'])
def create_assignment(student_id):
    """Create a new assignment"""
    data = request.get_json()
    
    required_fields = ['title', 'subject', 'due']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cursor = conn.execute(
        '''INSERT INTO assignments 
           (student_id, title, subject, due_date, status, difficulty, score)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (
            student_id,
            data['title'],
            data['subject'],
            data['due'],
            data.get('status', 'Pending'),
            data.get('difficulty', 'Medium'),
            data.get('score')
        )
    )
    
    assignment_id = cursor.lastrowid
    conn.commit()
    
    # Get the created assignment
    assignment = conn.execute(
        'SELECT * FROM assignments WHERE id = ?', (assignment_id,)
    ).fetchone()
    conn.close()
    
    return jsonify(dict(assignment)), 201

@app.route('/api/assignments/<int:assignment_id>', methods=['PUT'])
def update_assignment(assignment_id):
    """Update an existing assignment"""
    data = request.get_json()
    
    conn = get_db_connection()
    
    # Build dynamic update query
    update_fields = []
    values = []
    
    for field in ['title', 'subject', 'due_date', 'status', 'difficulty', 'score']:
        if field in data:
            update_fields.append(f"{field} = ?")
            values.append(data[field])
    
    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400
    
    values.append(assignment_id)
    query = f"UPDATE assignments SET {', '.join(update_fields)} WHERE id = ?"
    
    conn.execute(query, values)
    conn.commit()
    
    # Get updated assignment
    assignment = conn.execute(
        'SELECT * FROM assignments WHERE id = ?', (assignment_id,)
    ).fetchone()
    conn.close()
    
    if assignment:
        return jsonify(dict(assignment))
    else:
        return jsonify({'error': 'Assignment not found'}), 404

@app.route('/api/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    """Delete an assignment"""
    conn = get_db_connection()
    result = conn.execute(
        'DELETE FROM assignments WHERE id = ?', (assignment_id,)
    )
    conn.commit()
    conn.close()
    
    if result.rowcount > 0:
        return jsonify({'message': 'Assignment deleted successfully'})
    else:
        return jsonify({'error': 'Assignment not found'}), 404

# Chat Routes
@app.route('/api/chat/<student_id>', methods=['GET'])
def get_chat_history(student_id):
    """Get chat history for a student"""
    conn = get_db_connection()
    messages = conn.execute(
        'SELECT * FROM chat_messages WHERE student_id = ? ORDER BY timestamp ASC',
        (student_id,)
    ).fetchall()
    conn.close()
    
    return jsonify([{
        'sender': msg['sender'],
        'text': msg['message'],
        'timestamp': msg['timestamp']
    } for msg in messages])

@app.route('/api/chat/<student_id>', methods=['POST'])
def save_chat_message(student_id):
    """Save a chat message"""
    data = request.get_json()
    
    if 'sender' not in data or 'text' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO chat_messages (student_id, sender, message) VALUES (?, ?, ?)',
        (student_id, data['sender'], data['text'])
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'sender': data['sender'],
        'text': data['text'],
        'timestamp': datetime.now().isoformat()
    }), 201

# Gemini AI Chat Route
@app.route('/api/chat/<student_id>/ai', methods=['POST'])
def chat_with_ai(student_id):
    """Get AI response from Gemini"""
    data = request.get_json()
    message = data.get('message')
    # Load API key from environment (configured via .env)
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get conversation history for context
    conn = get_db_connection()
    history = conn.execute(
        'SELECT sender, message FROM chat_messages WHERE student_id = ? ORDER BY timestamp DESC LIMIT 10',
        (student_id,)
    ).fetchall()
    conn.close()
    
    # Generate AI response
    gemini = GeminiService(api_key)
    ai_response = gemini.generate_response(message, [dict(h) for h in history])
    
    # Save both user message and AI response
    conn = get_db_connection()
    
    # Save user message
    conn.execute(
        'INSERT INTO chat_messages (student_id, sender, message) VALUES (?, ?, ?)',
        (student_id, 'user', message)
    )
    
    # Save AI response
    conn.execute(
        'INSERT INTO chat_messages (student_id, sender, message) VALUES (?, ?, ?)',
        (student_id, 'ai', ai_response)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'response': ai_response,
        'timestamp': datetime.now().isoformat()
    })

# Image Upload and Chat Route
@app.route('/api/chat/<student_id>/ai/image', methods=['POST'])
def chat_with_ai_image(student_id):
    """Get AI response from Gemini with image input"""
    # Check if image file is present
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    message = request.form.get('message', 'What do you see in this image?')
    # Load API key from environment (configured via .env)
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if image_file.filename == '':
        return jsonify({'error': 'No image file selected'}), 400
    
    if not allowed_file(image_file.filename):
        return jsonify({'error': 'Invalid file type. Please upload an image file (PNG, JPG, JPEG, GIF, BMP, WEBP)'}), 400
    
    # Process the image
    image_base64 = process_image(image_file)
    if not image_base64:
        return jsonify({'error': 'Failed to process image'}), 400
    
    # Get conversation history for context
    conn = get_db_connection()
    history = conn.execute(
        'SELECT sender, message FROM chat_messages WHERE student_id = ? ORDER BY timestamp DESC LIMIT 10',
        (student_id,)
    ).fetchall()
    conn.close()
    
    # Generate AI response with image
    gemini = GeminiService(api_key)
    ai_response = gemini.generate_response_with_image(message, image_base64, [dict(h) for h in history])
    
    # Save both user message and AI response
    conn = get_db_connection()
    
    # Save user message (with indication that it included an image)
    user_message_text = f"{message} [Image uploaded]"
    conn.execute(
        'INSERT INTO chat_messages (student_id, sender, message) VALUES (?, ?, ?)',
        (student_id, 'user', user_message_text)
    )
    
    # Save AI response
    conn.execute(
        'INSERT INTO chat_messages (student_id, sender, message) VALUES (?, ?, ?)',
        (student_id, 'ai', ai_response)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'response': ai_response,
        'timestamp': datetime.now().isoformat()
    })

# Analytics and Progress Routes
@app.route('/api/progress/<student_id>', methods=['GET'])
def get_progress(student_id):
    """Get learning progress analytics"""
    conn = get_db_connection()
    
    # Assignment statistics
    assignment_stats = conn.execute('''
        SELECT 
            status,
            COUNT(*) as count
        FROM assignments 
        WHERE student_id = ? 
        GROUP BY status
    ''', (student_id,)).fetchall()
    
    # Subject performance
    subject_stats = conn.execute('''
        SELECT 
            subject,
            AVG(CASE WHEN score IS NOT NULL THEN score ELSE 0 END) as avg_score,
            COUNT(*) as total_assignments
        FROM assignments 
        WHERE student_id = ? 
        GROUP BY subject
    ''', (student_id,)).fetchall()
    
    # Chat activity
    chat_count = conn.execute(
        'SELECT COUNT(*) as count FROM chat_messages WHERE student_id = ?',
        (student_id,)
    ).fetchone()
    
    conn.close()
    
    return jsonify({
        'assignmentStats': [dict(stat) for stat in assignment_stats],
        'subjectPerformance': [dict(stat) for stat in subject_stats],
        'chatActivity': dict(chat_count)['count']
    })

# Student Subject Performance API
@app.route('/api/performance/<student_id>', methods=['GET'])
def get_student_performance(student_id):
    """Return per-subject performance time series for a student"""
    conn = get_db_connection()
    rows = conn.execute(
        '''SELECT subject, date, score
           FROM subject_performance
           WHERE student_id = ?
           ORDER BY date ASC''',
        (student_id,)
    ).fetchall()
    conn.close()

    # Group by subject
    data = {}
    for r in rows:
        subj = r['subject']
        data.setdefault(subj, []).append({
            'date': r['date'],
            'score': r['score']
        })
    return jsonify(data)

# Health check route
@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Tutorly API is running',
        'timestamp': datetime.now().isoformat()
    })

# Route to serve the main HTML file
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Route to serve the frontend at /static/ path
@app.route('/static/')
def static_index():
    return app.send_static_file('index.html')

# Route to serve favicon
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

# Error handlers
@app.errorhandler(404)
def not_found(_):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(_):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database on startup
    # Load environment variables from .env if present (without python-dotenv)
    try:
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
    except Exception as _e:
        # Non-fatal; continue with existing environment
        pass

    init_database()
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Tutorly API server on port {port}")
    print(f"Database: {DATABASE}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)