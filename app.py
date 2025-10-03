from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import PyPDF2
from docx import Document
import io
import re
import json
import pandas as pd
from flask import send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/blooms_taxonomy')
try:
    client = MongoClient(MONGO_URI)
    db = client.get_database()
    users_collection = db.users
    analyses_collection = db.analyses
    print("MongoDB connected successfully")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    # Create in-memory collections for testing
    users_collection = []
    analyses_collection = []

# JWT configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-here')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
REPORT_EXTENSIONS = {'xlsx', 'xls', 'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enhanced Bloom's Taxonomy levels with comprehensive keywords and descriptions
bloom_levels = {
    "L1-Remember": {
        "keywords": ["define", "describe", "identify", "list", "name", "recall", "recognize", "state", "tell", "what", "when", "where", "who", "which", "how many", "what is", "can you name", "find", "locate", "match", "select", "choose", "label", "memorize", "repeat", "reproduce", "retrieve", "write", "recite", "record", "relate", "underline", "arrange", "duplicate", "order", "quote", "cite", "enumerate", "tabulate", "specify", "mention", "point out", "show", "indicate", "pick", "spell", "count", "draw", "outline", "trace", "copy", "fill in", "complete", "mark", "tick", "circle", "highlight", "note", "jot down"],
        "description": "Recall facts and basic concepts",
        "color": "#FF6B6B"
    },
    "L2-Understand": {
        "keywords": ["explain", "describe", "discuss", "interpret", "summarize", "paraphrase", "translate", "illustrate", "demonstrate", "compare", "contrast", "classify", "categorize", "organize", "outline", "restate", "clarify", "elaborate", "give examples", "what does this mean", "how would you explain", "what is the main idea", "comprehend", "convert", "defend", "distinguish", "estimate", "extend", "generalize", "infer", "predict", "rewrite", "associate", "compute", "discuss", "express", "locate", "recognize", "report", "review", "transform", "characterize", "conclude", "differentiate", "expand", "interpolate", "rephrase", "substitute", "visualize", "decode", "decipher", "grasp", "perceive", "understand", "comprehend"],
        "description": "Explain ideas and concepts",
        "color": "#4ECDC4"
    },
    "L3-Apply": {
        "keywords": ["apply", "use", "implement", "solve", "calculate", "demonstrate", "execute", "perform", "show", "illustrate", "practice", "construct", "build", "create", "develop", "design", "produce", "make", "build", "how would you use", "what would happen if", "solve this problem", "apply this to", "employ", "utilize", "operate", "manipulate", "modify", "prepare", "relate", "schedule", "sketch", "dramatize", "experiment", "interview", "paint", "simulate", "adapt", "carry out", "complete", "examine", "exercise", "interpret", "model", "organize", "restructure", "role-play", "sequence", "transfer", "adopt", "capitalize on", "consume", "deploy", "handle", "put to use", "take advantage of", "work with"],
        "description": "Use information in new situations",
        "color": "#45B7D1"
    },
    "L4-Analyze": {
        "keywords": ["analyze", "examine", "investigate", "compare", "contrast", "differentiate", "distinguish", "examine", "explore", "identify", "infer", "outline", "structure", "organize", "relate", "connect", "break down", "classify", "categorize", "what are the parts", "how does this relate to", "what evidence", "what are the differences", "what are the similarities", "appraise", "calculate", "criticize", "discriminate", "examine", "experiment", "question", "test", "detect", "diagnose", "dissect", "illustrate", "inspect", "relate", "select", "separate", "subdivide", "survey", "take apart", "deconstruct", "parse", "scrutinize", "audit", "blueprint", "characterize", "correlate", "deduce", "determine", "diagram", "divide", "focus", "isolate", "limit", "prioritize", "reduce", "simplify", "uncover"],
        "description": "Draw connections among ideas",
        "color": "#96CEB4"
    },
    "L5-Evaluate": {
        "keywords": ["evaluate", "assess", "judge", "critique", "appraise", "rate", "rank", "grade", "score", "measure", "test", "examine", "review", "analyze", "compare", "contrast", "justify", "defend", "argue", "support", "what do you think about", "how would you rate", "what is your opinion", "is this good or bad", "what are the pros and cons", "conclude", "criticize", "decide", "discriminate", "prioritize", "recommend", "summarize", "validate", "verify", "award", "choose", "estimate", "interpret", "predict", "value", "weigh", "attach", "check", "monitor", "perceive", "prize", "select", "agree", "convince", "dispute", "influence", "persuade", "prove", "disprove", "assess merit", "determine value", "make judgment", "form opinion", "reach conclusion", "establish criteria", "set standards"],
        "description": "Justify a stand or decision",
        "color": "#FFEAA7"
    },
    "L6-Create": {
        "keywords": ["create", "design", "develop", "build", "construct", "produce", "make", "compose", "write", "draw", "paint", "sculpt", "invent", "formulate", "plan", "organize", "assemble", "generate", "compose", "what would you create", "how would you design", "what would you build", "can you make", "invent a solution", "combine", "compile", "devise", "modify", "originate", "rearrange", "reconstruct", "reorganize", "revise", "rewrite", "transform", "adapt", "anticipate", "collaborate", "communicate", "compare", "facilitate", "integrate", "intervene", "model", "negotiate", "propose", "synthesize", "systematize", "theorize", "validate", "establish", "fabricate", "fashion", "hypothesize", "incorporate", "initiate", "innovate", "institute", "network", "perform", "portray", "substitute"],
        "description": "Produce new or original work",
        "color": "#DDA0DD"
    }
}

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data.get('email', '')
        self.name = user_data.get('name', '')
        self.created_at = user_data.get('created_at', datetime.now())
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    from bson import ObjectId
    try:
        user_data = users_collection.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
    except:
        pass
    return None

def create_jwt_token(user_id):
    """Create JWT token for user - Fixed for Python compatibility"""
    # Use timezone.utc for Python 3.9+ compatibility
    try:
        from datetime import timezone
        utc_now = datetime.now(timezone.utc)
    except ImportError:
        # Fallback for older Python versions
        utc_now = datetime.utcnow()
    
    payload = {
        'user_id': user_id,
        'exp': utc_now + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': utc_now
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token):
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def save_analysis_to_db(user_id, analysis_type, content, results):
    """Save analysis results to MongoDB"""
    analysis_data = {
        'user_id': user_id,
        'analysis_type': analysis_type,
        'content': content,
        'results': results,
        'created_at': datetime.now()
    }
    try:
        if hasattr(analyses_collection, 'insert_one'):
            analyses_collection.insert_one(analysis_data)
            print(f"Analysis saved to database: {analysis_data}")
        else:
            print("MongoDB not available, analysis not saved")
    except Exception as e:
        print(f"Error saving analysis: {e}")

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_report_file(filename):
    """Check if the uploaded file has an allowed extension for reports"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in REPORT_EXTENSIONS

def read_questions_from_file(file_path, file_extension):
    """Read questions from Excel or CSV file"""
    questions = []
    
    try:
        if file_extension == 'csv':
            df = pd.read_csv(file_path)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(file_path)
        else:
            return []
        
        # Look for question column (case insensitive)
        question_col = None
        for col in df.columns:
            if col.lower().strip() in ['question', 'questions', 'q', 'query']:
                question_col = col
                break
        
        if question_col is None:
            # If no specific column found, use the first column
            question_col = df.columns[0]
        
        # Extract questions and clean them
        for idx, row in df.iterrows():
            question = str(row[question_col]).strip()
            if question and question.lower() != 'nan' and len(question) > 5:
                questions.append(question)
        
        return questions
    
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def create_report_file(questions_data, file_format='xlsx'):
    """Create Excel or CSV report with questions and Bloom's levels"""
    try:
        # Prepare data for DataFrame
        report_data = []
        for item in questions_data:
            report_data.append({
                'Question': item['question'],
                'Blooms_Level': item['level'],
                'Description': item['description']
            })
        
        df = pd.DataFrame(report_data)
        
        # Create temporary file
        import tempfile
        if file_format == 'xlsx':
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False)
        elif file_format == 'pdf':
            # Use the PDF generation function for PDF format
            return create_pdf_report(questions_data)
        else:  # csv
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            df.to_csv(temp_file.name, index=False)
        
        return temp_file.name
    
    except Exception as e:
        print(f"Error creating report file: {e}")
        return None

def create_pdf_report(questions_data, filename="blooms_report"):
    """Create an attractive PDF report with questions and Bloom's levels"""
    try:
        import tempfile
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import PageBreak
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
        # Create PDF document with margins
        doc = SimpleDocTemplate(
            temp_file.name, 
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        styles = getSampleStyleSheet()
        story = []
        
        # Define colors
        primary_color = HexColor('#2E86AB')
        secondary_color = HexColor('#A23B72')
        accent_color = HexColor('#F18F01')
        light_gray = HexColor('#F5F5F5')
        dark_gray = HexColor('#333333')
        
        # Title with modern styling
        title_style = ParagraphStyle(
            'ModernTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=10,
            spaceBefore=0,
            alignment=1,
            textColor=primary_color,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=40,
            alignment=1,
            textColor=dark_gray,
            fontName='Helvetica'
        )
        
        story.append(Paragraph("📊 Bloom's Taxonomy Analysis Report", title_style))
        story.append(Paragraph("Educational Assessment & Cognitive Level Classification", subtitle_style))
        
        # Define level colors for the questions table
        level_colors = {
            'L1-Remember': HexColor('#FF6B6B'),
            'L2-Understand': HexColor('#4ECDC4'),
            'L3-Apply': HexColor('#45B7D1'),
            'L4-Analyze': HexColor('#96CEB4'),
            'L5-Evaluate': HexColor('#FFEAA7'),
            'L6-Create': HexColor('#DDA0DD')
        }
        
        # Section header style
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=10,
            textColor=secondary_color,
            fontName='Helvetica-Bold'
        )
        
        # Detailed questions section
        story.append(Paragraph("📝 Detailed Question Analysis", section_style))
        
        # Create questions table with better formatting and multi-level support
        questions_table_data = [['#', 'Question', 'Bloom\'s Level']]
        
        for i, item in enumerate(questions_data, 1):
            question_text = item['question']
            
            # Use Paragraph for proper text wrapping instead of truncating
            question_paragraph = Paragraph(question_text, styles['Normal'])
            
            # Handle multi-level display
            level_display = item.get('level_display', item['level'])
            if item.get('is_multi_level', False):
                level_display = f"🔄 {level_display}"  # Add multi-level indicator
            
            questions_table_data.append([
                str(i),
                question_paragraph,  # Use paragraph for proper wrapping
                level_display
            ])
        
        questions_table = Table(questions_table_data, colWidths=[0.3*inch, 5.0*inch, 1.5*inch])
        
        # Enhanced table styling
        table_style = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), secondary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Question numbers
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # Bloom's levels
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # Questions
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F9F9F9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey)
        ]
        
        # Add level-specific colors for Bloom's level column
        for i, original_item in enumerate(questions_data, 1):
            if isinstance(original_item, dict):
                level = original_item.get('level', '')
                if level in level_colors:
                    table_style.append(('BACKGROUND', (2, i), (2, i), level_colors[level]))
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.white))
                    table_style.append(('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'))
        
        questions_table.setStyle(TableStyle(table_style))
        story.append(questions_table)
        
        # Enhanced footer
        story.append(Spacer(1, 40))
        
        footer_info_style = ParagraphStyle(
            'FooterInfo',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,
            textColor=dark_gray,
            spaceAfter=5
        )
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            alignment=1,
            textColor=colors.grey
        )
        
        # Build PDF
        doc.build(story)
        return temp_file.name
        
    except Exception as e:
        print(f"Error creating PDF report: {e}")
        return None

def extract_text_from_file(file_path, file_extension):
    """Extract text from different file types"""
    text = ""
    
    try:
        if file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        
        elif file_extension == 'pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        
        elif file_extension in ['docx', 'doc']:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        
        return text.strip()
    
    except Exception as e:
        print(f"Error extracting text from file: {e}")
        return ""

def extract_questions_from_text(text):
    """Extract individual questions from text"""
    # Split by common question patterns
    question_patterns = [
        r'\d+\.\s*[A-Z][^.!?]*[.!?]',  # Numbered questions
        r'[A-Z][^.!?]*\?',  # Questions ending with ?
        r'Q\d+\.\s*[A-Z][^.!?]*[.!?]',  # Q1, Q2, etc.
        r'Question\s*\d+\.\s*[A-Z][^.!?]*[.!?]',  # Question 1, etc.
        r'[A-Z][^.!?]*\s*\([^)]*\)[^.!?]*[.!?]',  # Questions with options
    ]
    
    questions = []
    
    # First, try to find structured questions
    for pattern in question_patterns:
        matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
        questions.extend(matches)
    
    # If no structured questions found, split by sentences that look like questions
    if not questions:
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and any(keyword in sentence.lower() for keyword in 
                ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'explain', 'describe', 'analyze', 'evaluate', 'compare', 'contrast']):
                questions.append(sentence)
    
    # Clean up questions
    cleaned_questions = []
    for question in questions:
        question = question.strip()
        if len(question) > 5:  # Minimum length
            cleaned_questions.append(question)
    
    return cleaned_questions

def classify_question(question, return_multiple=False):
    """Classify a question into Bloom's Taxonomy levels with multi-level detection"""
    question_lower = question.lower().strip()
    
    # Enhanced keyword matching with weighted scoring
    level_scores = {
        "L1-Remember": 0,
        "L2-Understand": 0,
        "L3-Apply": 0,
        "L4-Analyze": 0,
        "L5-Evaluate": 0,
        "L6-Create": 0
    }
    
    # High-priority keywords that strongly indicate specific levels
    strong_indicators = {
        "L1-Remember": ["what is", "define", "list", "name", "identify", "recall", "state", "who", "when", "where", "cite", "enumerate", "specify", "mention"],
        "L2-Understand": ["explain", "describe", "interpret", "summarize", "paraphrase", "discuss", "outline", "clarify", "comprehend", "convert", "translate", "illustrate"],
        "L3-Apply": ["apply", "use", "implement", "solve", "calculate", "demonstrate", "show", "illustrate", "practice", "employ", "utilize", "execute", "perform"],
        "L4-Analyze": ["analyze", "examine", "compare", "contrast", "differentiate", "investigate", "break down", "categorize", "dissect", "deconstruct", "scrutinize"],
        "L5-Evaluate": ["evaluate", "assess", "judge", "critique", "rate", "justify", "argue", "defend", "support", "appraise", "validate", "criticize"],
        "L6-Create": ["create", "design", "develop", "build", "construct", "produce", "make", "compose", "generate", "invent", "formulate", "devise"]
    }
    
    # Check for strong indicators first (higher weight)
    for level, keywords in strong_indicators.items():
        for keyword in keywords:
            if keyword in question_lower:
                level_scores[level] += 4  # Higher weight for strong indicators
    
    # Check regular keywords from bloom_levels
    for level, data in bloom_levels.items():
        for keyword in data["keywords"]:
            if keyword.lower() in question_lower:
                level_scores[level] += 1
    
    # Multi-level detection: questions that span multiple levels
    total_score = sum(level_scores.values())
    
    if return_multiple and total_score > 0:
        # Return multiple levels if they have significant scores
        threshold = max(level_scores.values()) * 0.6  # 60% of max score
        multiple_levels = []
        
        for level, score in level_scores.items():
            if score >= threshold and score > 0:
                multiple_levels.append({
                    'level': level,
                    'score': score,
                    'description': bloom_levels[level]['description'],
                    'color': bloom_levels[level]['color']
                })
        
        # Sort by score (highest first)
        multiple_levels.sort(key=lambda x: x['score'], reverse=True)
        
        if len(multiple_levels) > 1:
            return multiple_levels
    
    # Single level classification (original behavior)
    max_score = max(level_scores.values())
    
    if max_score == 0:
        # Default classification based on question structure
        if any(word in question_lower for word in ["what", "who", "when", "where", "which"]):
            best_level = "L1-Remember"
        elif any(word in question_lower for word in ["how", "why", "explain"]):
            best_level = "L2-Understand"
        else:
            best_level = "L1-Remember"
    else:
        best_level = max(level_scores, key=level_scores.get)
    
    if return_multiple:
        return [{
            'level': best_level,
            'score': max_score,
            'description': bloom_levels[best_level]['description'],
            'color': bloom_levels[best_level]['color']
        }]
    
    return best_level

def analyze_question_paper(questions):
    """Analyze a complete question paper and provide statistics with multi-level detection"""
    results = []
    level_counts = {level: 0 for level in bloom_levels.keys()}
    multi_level_questions = []
    total_questions = len(questions)
    
    for i, question in enumerate(questions, 1):
        # Try multi-level classification first
        multi_levels = classify_question(question, return_multiple=True)
        
        if len(multi_levels) > 1:
            # Multi-level question
            primary_level = multi_levels[0]['level']
            level_counts[primary_level] += 1
            
            # Create display string for multiple levels
            level_display = " + ".join([ml['level'].split('-')[1] for ml in multi_levels])
            
            results.append({
                'question_number': i,
                'question': question,
                'level': primary_level,
                'level_display': level_display,
                'description': bloom_levels[primary_level]['description'],
                'color': bloom_levels[primary_level]['color'],
                'is_multi_level': True,
                'all_levels': multi_levels
            })
            
            multi_level_questions.append({
                'question_number': i,
                'question': question,
                'levels': multi_levels
            })
        else:
            # Single level question (traditional)
            level = classify_question(question)
            level_counts[level] += 1
            
            results.append({
                'question_number': i,
                'question': question,
                'level': level,
                'level_display': level.split('-')[1],
                'description': bloom_levels[level]['description'],
                'color': bloom_levels[level]['color'],
                'is_multi_level': False,
                'all_levels': [multi_levels[0]] if multi_levels else []
            })
    
    # Calculate percentages
    level_percentages = {}
    for level, count in level_counts.items():
        percentage = (count / total_questions * 100) if total_questions > 0 else 0
        level_percentages[level] = {
            'count': count,
            'percentage': round(percentage, 1)
        }
    
    return {
        'total_questions': total_questions,
        'level_counts': level_counts,
        'level_percentages': level_percentages,
        'questions': results,
        'multi_level_questions': multi_level_questions,
        'multi_level_count': len(multi_level_questions)
    }

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user_data = users_collection.find_one({'email': email})
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user, remember=True)
            token = create_jwt_token(str(user_data['_id']))
            return jsonify({'success': True, 'token': token, 'redirect': url_for('dashboard')})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        # Check if user already exists
        if users_collection.find_one({'email': email}):
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        # Create new user
        user_data = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': datetime.now()
        }
        
        result = users_collection.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        
        user = User(user_data)
        login_user(user, remember=True)
        token = create_jwt_token(str(user_data['_id']))
        return jsonify({'success': True, 'token': token, 'redirect': url_for('dashboard')})
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent analyses for the current user
    try:
        if hasattr(analyses_collection, 'find'):
            recent_analyses = list(analyses_collection.find(
                {'user_id': current_user.id}
            ).sort('created_at', -1).limit(5))
        else:
            recent_analyses = []
    except Exception as e:
        print(f"Error fetching analyses: {e}")
        recent_analyses = []
    
    return render_template('dashboard.html', recent_analyses=recent_analyses)

@app.route('/classifier')
@login_required
def classifier():
    return render_template('classifier.html')

@app.route('/classify', methods=['POST'])
@login_required
def classify():
    data = request.get_json()
    question = data.get('question', '').strip()
    
    print(f"Received question: {question}")
    
    if not question:
        return jsonify({'error': 'Please provide a question'})
    
    level = classify_question(question)
    level_data = bloom_levels[level]
    
    # Save to database
    save_analysis_to_db(
        current_user.id,
        'single_question',
        question,
        {'level': level}
    )
    
    return jsonify({
        'success': True,
        'level': level,
        'description': level_data['description'],
        'color': level_data['color'],
        'question': question
    })

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload and analyze question paper"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text from file
        file_extension = filename.rsplit('.', 1)[1].lower()
        text = extract_text_from_file(file_path, file_extension)
        
        if not text:
            return jsonify({'error': 'Could not extract text from the uploaded file'})
        
        # Extract questions from text
        questions = extract_questions_from_text(text)
        
        if not questions:
            return jsonify({'error': 'No questions found in the uploaded file'})
        
        # Analyze the question paper
        analysis = analyze_question_paper(questions)
        
        # Save to database
        save_analysis_to_db(
            current_user.id,
            'file_upload',
            text,
            analysis
        )
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'filename': filename,
            'analysis': analysis
        })
    
    return jsonify({'error': 'Invalid file type. Please upload .txt, .pdf, .docx, or .doc files'})

@app.route('/upload_report', methods=['POST'])
@login_required
def upload_report_file():
    """Handle Excel/CSV file upload for report generation"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file and allowed_report_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract questions from file
        file_extension = filename.rsplit('.', 1)[1].lower()
        questions = read_questions_from_file(file_path, file_extension)
        
        if not questions:
            return jsonify({'error': 'No questions found in the uploaded file. Please ensure your file has a "Question" column or questions in the first column.'})
        
        # Classify each question
        classified_questions = []
        level_counts = {level: 0 for level in bloom_levels.keys()}
        
        for i, question in enumerate(questions, 1):
            level = classify_question(question)
            level_counts[level] += 1
            
            classified_questions.append({
                'question_number': i,
                'question': question,
                'level': level,
                'description': bloom_levels[level]['description'],
                'color': bloom_levels[level]['color']
            })
        
        # Calculate statistics
        total_questions = len(questions)
        level_percentages = {}
        for level, count in level_counts.items():
            percentage = (count / total_questions * 100) if total_questions > 0 else 0
            level_percentages[level] = {
                'count': count,
                'percentage': round(percentage, 1)
            }
        
        analysis_result = {
            'total_questions': total_questions,
            'level_counts': level_counts,
            'level_percentages': level_percentages,
            'questions': classified_questions
        }
        
        # Save to database
        save_analysis_to_db(
            current_user.id,
            'report_upload',
            f'Excel/CSV file: {filename}',
            analysis_result
        )
        
        # Store in session for download
        session['report_data'] = classified_questions
        session['report_filename'] = filename
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'filename': filename,
            'analysis': analysis_result
        })
    
    return jsonify({'error': 'Invalid file type. Please upload .xlsx, .xls, or .csv files'})

@app.route('/download_report/<format>')
@login_required
def download_report(format):
    """Generate and download report in Excel, CSV, or PDF format"""
    if 'report_data' not in session:
        return jsonify({'error': 'No report data available. Please upload a file first.'})
    
    questions_data = session['report_data']
    original_filename = session.get('report_filename', 'questions')
    
    # Remove extension from original filename
    base_filename = original_filename.rsplit('.', 1)[0]
    
    # Create report file
    report_file_path = create_report_file(questions_data, format)
    
    if not report_file_path:
        return jsonify({'error': 'Failed to generate report file'})
    
    # Set download filename
    download_filename = f"{base_filename}_blooms_report.{format}"
    
    # Set appropriate MIME type
    if format == 'xlsx':
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif format == 'pdf':
        mimetype = 'application/pdf'
    else:  # csv
        mimetype = 'text/csv'
    
    try:
        return send_file(
            report_file_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype=mimetype
        )
    except Exception as e:
        return jsonify({'error': f'Failed to download file: {str(e)}'})
    finally:
        # Clean up temporary file
        try:
            os.remove(report_file_path)
        except:
            pass

@app.route('/api/levels')
def get_levels():
    return jsonify(bloom_levels)

if __name__ == '__main__':
    app.run(debug=True)
