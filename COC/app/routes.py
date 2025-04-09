from flask import render_template, flash, redirect, url_for, request, session, jsonify
from werkzeug.utils import secure_filename
from app import app
from app.processor import (
    validate_pdf,
    detect_document_type,
    extract_jabil_data,
    extract_elcam_data,
    compare_documents
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
            
            try:
                # Process the documents
                results = process_documents(file1_path, file2_path)
                
                # Store results in session
                session['results'] = results
                
                return redirect(url_for('results'))
            except Exception as e:
                flash(f'Error processing documents: {str(e)}')
                return redirect(request.url)
        else:
            flash('Only PDF files are allowed')
    
    return render_template('index.html')

def process_documents(file1_path, file2_path):
    """
    Process the two uploaded documents, identify their types,
    extract data directly using the pdf_processor functions,
    and compare them.
    """
    results = {
        'doc1': {
            'file_path': os.path.basename(file1_path)
        },
        'doc2': {
            'file_path': os.path.basename(file2_path)
        },
        'comparison': None
    }
    
    # Hard-code document types for testing
    # Based on common document filenames or simply assign one of each type
    # for files where type can't be determined from filename
    
    # Determine types from filenames when possible
    # For testing: if filename doesn't clearly indicate type, assume doc1=Jabil, doc2=Elcam
    filename1 = os.path.basename(file1_path).lower()
    filename2 = os.path.basename(file2_path).lower()
    
    # Use the new detect_document_type function
    results['doc1']['type'] = detect_document_type(file1_path)
    results['doc2']['type'] = detect_document_type(file2_path)
    
    # Ensure we have one of each type for proper comparison
    # If both are the same type or unknown, assign one of each
    if (results['doc1']['type'] == results['doc2']['type'] or 
        results['doc1']['type'] == 'Unknown' or 
        results['doc2']['type'] == 'Unknown'):
        print("Couldn't detect distinct document types, assigning defaults")
        results['doc1']['type'] = 'Jabil'
        results['doc2']['type'] = 'Elcam'
    
    print(f"Document 1 type: {results['doc1']['type']}")
    print(f"Document 2 type: {results['doc2']['type']}")
    
    # Extract data based on document types
    jabil_data = None
    elcam_data = None
    
    # Process document 1
    try:
        if results['doc1']['type'] == 'Jabil':
            print(f"Extracting Jabil data from document 1")
            # Use the function from the new processor module
            jabil_result = extract_jabil_data(file1_path)
            print(f"Jabil extraction result: {jabil_result}")
            results['doc1']['data'] = jabil_result
            jabil_data = results['doc1']['data']
        elif results['doc1']['type'] == 'Elcam':
            print(f"Extracting Elcam data from document 1")
            # Use the function from the new processor module
            elcam_result = extract_elcam_data(file1_path)
            print(f"Elcam extraction result: {elcam_result}")
            results['doc1']['data'] = elcam_result
            elcam_data = results['doc1']['data']
        else:
            results['doc1']['data'] = {"error": f"Unknown document type: {results['doc1']['type']}"}
    except Exception as e:
        print(f"Error processing document 1: {str(e)}")
        results['doc1']['data'] = {"error": f"Processing error: {str(e)}"}
    
    # Process document 2
    try:
        if results['doc2']['type'] == 'Jabil':
            print(f"Extracting Jabil data from document 2")
            # Use the function from the new processor module
            jabil_result = extract_jabil_data(file2_path)
            print(f"Jabil extraction result: {jabil_result}")
            results['doc2']['data'] = jabil_result
            jabil_data = results['doc2']['data']
        elif results['doc2']['type'] == 'Elcam':
            print(f"Extracting Elcam data from document 2")
            # Use the function from the new processor module
            elcam_result = extract_elcam_data(file2_path)
            print(f"Elcam extraction result: {elcam_result}")
            results['doc2']['data'] = elcam_result
            elcam_data = results['doc2']['data']
        else:
            results['doc2']['data'] = {"error": f"Unknown document type: {results['doc2']['type']}"}
    except Exception as e:
        print(f"Error processing document 2: {str(e)}")
        results['doc2']['data'] = {"error": f"Processing error: {str(e)}"}
    
    # If we have both Jabil and Elcam documents, compare them
    try:
        print(f"Jabil data: {jabil_data}")
        print(f"Elcam data: {elcam_data}")
        
        if jabil_data and elcam_data:
            # Check if either has an error
            if 'error' in jabil_data or 'error' in elcam_data:
                results['comparison'] = {"error": "Cannot compare documents with errors"}
            else:
                # Attempt comparison
                comparison_result = compare_documents(jabil_data, elcam_data)
                print(f"Comparison result: {comparison_result}")
                results['comparison'] = comparison_result
        else:
            results['comparison'] = {"error": "Need one Jabil and one Elcam document to compare"}
    except Exception as e:
        print(f"Error in document comparison: {str(e)}")
        results['comparison'] = {"error": f"Comparison error: {str(e)}"}
    
    return results

@app.route('/results')
def results():
    if 'results' not in session:
        return redirect(url_for('index'))
    
    # Ensure we have valid results with all required fields
    results = session['results']
    
    # Initialize empty dictionaries for missing fields to prevent template errors
    if 'doc1' not in results:
        results['doc1'] = {}
    if 'doc2' not in results:
        results['doc2'] = {}
    
    # Ensure type field exists
    if 'type' not in results['doc1']:
        results['doc1']['type'] = 'Unknown'
    if 'type' not in results['doc2']:
        results['doc2']['type'] = 'Unknown'
    
    # Ensure file_path field exists
    if 'file_path' not in results['doc1']:
        results['doc1']['file_path'] = 'No file'
    if 'file_path' not in results['doc2']:
        results['doc2']['file_path'] = 'No file'
    
    # Ensure data isn't None
    if results['doc1'].get('data') is None:
        results['doc1']['data'] = {'error': 'No data available'}
    if results['doc2'].get('data') is None:
        results['doc2']['data'] = {'error': 'No data available'}
        
    return render_template('results.html', results=results)
    
@app.route('/json_results')
def json_results():
    """
    Display the raw JSON results from the API calls
    """
    if 'results' not in session:
        return jsonify({'error': 'No results available'})
    
    return jsonify(session['results'])