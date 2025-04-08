from flask import render_template, flash, redirect, url_for, request, session
from werkzeug.utils import secure_filename
from app import app
from app.pdf_processor import validate_pdf, extract_pdf_fields
import os

# Configure upload folder
UPLOAD_FOLDER = 'app/uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.secret_key = 'your-secret-key-here'  # Change this in production

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file parts
        if 'file1' not in request.files or 'file2' not in request.files:
            flash('Both PDF files are required')
            return redirect(request.url)
            
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        # If user does not select files, browser submits empty files
        if file1.filename == '' or file2.filename == '':
            flash('Both PDF files must be selected')
            return redirect(request.url)
            
        if file1 and file2 and validate_pdf(file1) and validate_pdf(file2):
            # Save files
            filename1 = secure_filename(file1.filename)
            filename2 = secure_filename(file2.filename)
            file1_path = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
            file2_path = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
            file1.save(file1_path)
            file2.save(file2_path)
            
            # Extract data from PDFs
            results = {}
            results['file1'] = extract_pdf_fields(file1_path)
            results['file2'] = extract_pdf_fields(file2_path)
            
            # Store results in session
            session['results'] = results
            
            return redirect(url_for('results'))
        else:
            flash('Only PDF files are allowed')
    
    return render_template('index.html')

@app.route('/results')
def results():
    if 'results' not in session:
        return redirect(url_for('index'))
        
    return render_template('results.html', results=session['results'])
