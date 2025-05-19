import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import uuid
import tempfile
from chat_analyzer import analyze_chat_log
from models import db, ChatAnalysis, Keyword

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL is None:
    logger.error("DATABASE_URL environment variable is not set!")
    # Use a fallback SQLite database for development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat_analysis.db"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
logger.debug(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Initialize the database
db.init_app(app)

# Temp directory for file uploads
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create database tables
with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    # Get all analysis records from the database, ordered by most recent first
    analyses = ChatAnalysis.query.order_by(ChatAnalysis.created_at.desc()).all()
    return render_template('history.html', analyses=analyses)

@app.route('/how_it_works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Add debug logging
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request files: {request.files}")
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        logger.error("No file part in the request")
        flash('No file part', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['file']
    logger.debug(f"File name: {file.filename}")
    logger.debug(f"File content type: {file.content_type}")
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        logger.error("Empty filename submitted")
        flash('No selected file', 'danger')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filepath = None
        try:
            # Generate a unique filename to avoid collisions
            if file.filename is None:
                # Handle None filename (shouldn't happen but adding as a precaution)
                safe_filename = "unnamed.txt"
            else:
                safe_filename = secure_filename(file.filename)
                
            unique_filename = str(uuid.uuid4()) + "_" + safe_filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            logger.debug(f"Saving file to: {filepath}")
            
            # Save the file temporarily
            file.save(filepath)
            logger.debug(f"File saved successfully")
            
            # Check if file exists and has content
            if not os.path.exists(filepath):
                raise Exception("File could not be saved")
                
            file_size = os.path.getsize(filepath)
            logger.debug(f"File size: {file_size} bytes")
            
            if file_size == 0:
                raise Exception("Uploaded file is empty")
            
            # Analyze the chat log
            logger.debug(f"Starting analysis")
            analysis_results = analyze_chat_log(filepath)
            logger.debug(f"Analysis completed: {analysis_results}")
            
            # Save analysis results to database
            try:
                # Create a new ChatAnalysis record using the helper method
                chat_analysis = ChatAnalysis.from_analysis_results(safe_filename, analysis_results)
                
                # Add keywords
                for keyword in analysis_results['keywords']:
                    keyword_obj = Keyword()
                    keyword_obj.word = keyword
                    chat_analysis.keywords.append(keyword_obj)
                
                # Save to database
                db.session.add(chat_analysis)
                db.session.commit()
                logger.debug(f"Analysis saved to database with ID: {chat_analysis.id}")
                
                # Store the database ID in the session for redirecting to the right result
                session['analysis_id'] = chat_analysis.id
            except Exception as db_error:
                logger.error(f"Database error: {str(db_error)}")
                import traceback
                logger.error(traceback.format_exc())
                # Continue even if database save fails - we'll use the session-based results
                
            # Delete the temporary file
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"Temporary file removed")
            
            # Store results in session as fallback
            session['analysis_results'] = analysis_results
            logger.debug(f"Results stored in session")
            
            return redirect(url_for('results'))
        except Exception as e:
            logger.error(f"Error analyzing file: {str(e)}")
            logger.error(f"Exception details: {type(e).__name__}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Clean up on error (if file exists)
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"Cleaned up temporary file after error")
            
            flash(f'Error analyzing file: {str(e)}', 'danger')
            return redirect(url_for('index'))
    else:
        logger.error(f"Invalid file type: {file.filename}")
        flash('File type not allowed. Please upload a .txt file.', 'danger')
        return redirect(url_for('index'))

@app.route('/results')
@app.route('/results/<int:id>')
def results(id=None):
    # Check if we have a specific analysis ID
    if id:
        # Try to get the analysis from the database
        analysis = ChatAnalysis.query.get(id)
        if not analysis:
            flash('Analysis not found', 'danger')
            return redirect(url_for('index'))
        
        # Convert database model to dictionary format expected by template
        results = analysis.to_dict()
    else:
        # Fall back to session data if no id provided
        analysis_id = session.get('analysis_id')
        
        # If we have an analysis ID in the session, try to get from database
        if analysis_id:
            analysis = ChatAnalysis.query.get(analysis_id)
            if analysis:
                results = analysis.to_dict()
            else:
                # Fall back to session results if analysis_id not found
                results = session.get('analysis_results')
        else:
            # Just use session results
            results = session.get('analysis_results')
        
        # If no results found in either case, redirect with message
        if not results:
            flash('No analysis results found. Please upload a file first.', 'warning')
            return redirect(url_for('index'))
    
    logger.debug(f"Rendering results with: {results}")
    return render_template('summary.html', results=results)

@app.route('/sample')
def sample():
    try:
        # Path to the sample chat file
        sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_chat.txt')
        
        # Analyze the sample chat log
        analysis_results = analyze_chat_log(sample_path)
        
        # Save analysis results to database
        try:
            # Create a new ChatAnalysis record using the helper method
            chat_analysis = ChatAnalysis.from_analysis_results('sample_chat.txt', analysis_results)
            
            # Add keywords
            for keyword in analysis_results['keywords']:
                keyword_obj = Keyword()
                keyword_obj.word = keyword
                chat_analysis.keywords.append(keyword_obj)
            
            # Save to database
            db.session.add(chat_analysis)
            db.session.commit()
            logger.debug(f"Sample analysis saved to database with ID: {chat_analysis.id}")
            
            # Store the database ID in the session for redirecting to the right result
            session['analysis_id'] = chat_analysis.id
        except Exception as db_error:
            logger.error(f"Database error when saving sample: {str(db_error)}")
            import traceback
            logger.error(traceback.format_exc())
            # Continue even if database save fails - we'll use the session-based results
        
        # Store results in session as fallback
        session['analysis_results'] = analysis_results
        
        return redirect(url_for('results'))
    except Exception as e:
        logger.error(f"Error analyzing sample: {str(e)}")
        logger.error(f"Exception details: {type(e).__name__}")
        import traceback
        logger.error(traceback.format_exc())
        flash(f'Error analyzing sample: {str(e)}', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
