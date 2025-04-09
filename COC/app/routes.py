from flask import render_template, flash, redirect, url_for, request, session, jsonify
from werkzeug.utils import secure_filename
from app import app
from app.processor import (
    validate_pdf,
    jabil_or_elcam_invoice
)
import os
import json

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
        results = {}
        
        # Process file 1 if provided
        if 'file1' in request.files:
            file1 = request.files['file1']
            if file1.filename != '' and validate_pdf(file1):
                filename1 = secure_filename(file1.filename)
                file1_path = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
                file1.save(file1_path)
                
                try:
                    # Process file 1
                    results['file1'] = {
                        'filename': filename1,
                        'result': jabil_or_elcam_invoice(file1_path)
                    }
                except Exception as e:
                    results['file1'] = {
                        'filename': filename1,
                        'error': str(e)
                    }
            elif file1.filename != '':
                results['file1'] = {
                    'filename': file1.filename,
                    'error': 'Not a valid PDF file'
                }
        
        # Process file 2 if provided
        if 'file2' in request.files:
            file2 = request.files['file2']
            if file2.filename != '' and validate_pdf(file2):
                filename2 = secure_filename(file2.filename)
                file2_path = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
                file2.save(file2_path)
                
                try:
                    # Process file 2
                    results['file2'] = {
                        'filename': filename2,
                        'result': jabil_or_elcam_invoice(file2_path)
                    }
                except Exception as e:
                    results['file2'] = {
                        'filename': filename2,
                        'error': str(e)
                    }
            elif file2.filename != '':
                results['file2'] = {
                    'filename': file2.filename,
                    'error': 'Not a valid PDF file'
                }
        
        # Return the results
        if results:
            return jsonify(results)
        else:
            return jsonify({'error': 'No files were uploaded'})
    
    return render_template('index.html')