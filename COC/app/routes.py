from flask import render_template, flash, redirect, url_for, request, session, jsonify
from werkzeug.utils import secure_filename
from app import app
from app.pdf_processor import validate_pdf, extract_pdf_fields
from app.document_processor import (
    jabil_or_elcam_invoice,
    exctract_invoice_data_form_jabil_invoice,
    extract_elcam_invoice_data,
    compare_documents,
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
    extract data, and compare them.
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
    
    # Identify document types
    try:
        # Add debug print to see what's being returned
        print(f"Processing document 1: {file1_path}")
        doc1_type_result = jabil_or_elcam_invoice(file1_path)
        print(f"Document 1 type result: {doc1_type_result}")
        
        # Set a default type as a fallback
        results['doc1']['type'] = 'Unknown'
        
        # Try to extract invoice_type from the result, with multiple handling approaches
        if doc1_type_result is not None:
            if isinstance(doc1_type_result, dict) and 'invoice_type' in doc1_type_result:
                results['doc1']['type'] = doc1_type_result['invoice_type']
            elif hasattr(doc1_type_result, 'invoice_type'):
                results['doc1']['type'] = doc1_type_result.invoice_type
            elif isinstance(doc1_type_result, str):
                # If it's a string, just use that as the type
                results['doc1']['type'] = doc1_type_result
    except Exception as e:
        print(f"Error identifying doc1 type: {str(e)}")
        results['doc1']['type'] = 'Unknown'
    
    try:
        # Add debug print to see what's being returned
        print(f"Processing document 2: {file2_path}")
        doc2_type_result = jabil_or_elcam_invoice(file2_path)
        print(f"Document 2 type result: {doc2_type_result}")
        
        # Set a default type as a fallback
        results['doc2']['type'] = 'Unknown'
        
        # Try to extract invoice_type from the result, with multiple handling approaches
        if doc2_type_result is not None:
            if isinstance(doc2_type_result, dict) and 'invoice_type' in doc2_type_result:
                results['doc2']['type'] = doc2_type_result['invoice_type']
            elif hasattr(doc2_type_result, 'invoice_type'):
                results['doc2']['type'] = doc2_type_result.invoice_type
            elif isinstance(doc2_type_result, str):
                # If it's a string, just use that as the type
                results['doc2']['type'] = doc2_type_result
    except Exception as e:
        print(f"Error identifying doc2 type: {str(e)}")
        results['doc2']['type'] = 'Unknown'
    
    # Extract data based on document types
    jabil_data = None
    elcam_data = None
    
    # Process document 1
    try:
        if results['doc1']['type'] == 'Jabil':
            print(f"Extracting Jabil data from document 1")
            jabil_result = exctract_invoice_data_form_jabil_invoice(file1_path)
            print(f"Jabil extraction result: {jabil_result}")
            results['doc1']['data'] = jabil_result
            jabil_data = results['doc1']['data']
        elif results['doc1']['type'] == 'Elcam':
            print(f"Extracting Elcam data from document 1")
            elcam_result = extract_elcam_invoice_data(file1_path)
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
            jabil_result = exctract_invoice_data_form_jabil_invoice(file2_path)
            print(f"Jabil extraction result: {jabil_result}")
            results['doc2']['data'] = jabil_result
            jabil_data = results['doc2']['data']
        elif results['doc2']['type'] == 'Elcam':
            print(f"Extracting Elcam data from document 2")
            elcam_result = extract_elcam_invoice_data(file2_path)
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
        
    return render_template('results.html', results=results)