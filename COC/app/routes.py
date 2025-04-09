from flask import render_template, flash, redirect, url_for, request, session, jsonify
from werkzeug.utils import secure_filename
from app import app
from app.processor import (
    validate_pdf,
    jabil_or_elcam_invoice,
    extract_jabil_data,
    extract_elcam_data,
    generate_system_prompt,
    analyze_with_openai
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
                    # Process file 1 - first determine type
                    doc_type_result = jabil_or_elcam_invoice(file1_path)
                    
                    results['file1'] = {
                        'filename': filename1,
                        'result': doc_type_result
                    }
                    
                    # Handle both string and dictionary results
                    invoice_type = ''
                    if isinstance(doc_type_result, dict):
                        invoice_type = doc_type_result.get('invoice_type', '').lower()
                    elif isinstance(doc_type_result, str):
                        if 'jabil' in doc_type_result.lower():
                            invoice_type = 'jabil'
                        elif 'elcam' in doc_type_result.lower():
                            invoice_type = 'elcam'
                        
                    # Extract detailed data based on invoice type
                    if invoice_type == 'jabil':
                        jabil_data = extract_jabil_data(file1_path)
                        results['file1']['detailed_data'] = jabil_data
                    elif invoice_type == 'elcam':
                        elcam_data = extract_elcam_data(file1_path)
                        results['file1']['detailed_data'] = elcam_data
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
                    # Process file 2 - first determine type
                    doc_type_result = jabil_or_elcam_invoice(file2_path)
                    
                    results['file2'] = {
                        'filename': filename2,
                        'result': doc_type_result
                    }
                    
                    # Handle both string and dictionary results
                    invoice_type = ''
                    if isinstance(doc_type_result, dict):
                        invoice_type = doc_type_result.get('invoice_type', '').lower()
                    elif isinstance(doc_type_result, str):
                        if 'jabil' in doc_type_result.lower():
                            invoice_type = 'jabil'
                        elif 'elcam' in doc_type_result.lower():
                            invoice_type = 'elcam'
                        
                    # Extract detailed data based on invoice type
                    if invoice_type == 'jabil':
                        jabil_data = extract_jabil_data(file2_path)
                        results['file2']['detailed_data'] = jabil_data
                    elif invoice_type == 'elcam':
                        elcam_data = extract_elcam_data(file2_path)
                        results['file2']['detailed_data'] = elcam_data
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
        
        # Generate system prompt if both files have data
        if ('file1' in results and 'detailed_data' in results.get('file1', {}) and
            'file2' in results and 'detailed_data' in results.get('file2', {})):
            
            # Format document data for comparison
            doc1_data = {
                'document_type': (results['file1'].get('result', {}).get('invoice_type') 
                                  if isinstance(results['file1'].get('result'), dict) 
                                  else results['file1'].get('result')),
                'detailed_data': results['file1'].get('detailed_data')
            }
            
            doc2_data = {
                'document_type': (results['file2'].get('result', {}).get('invoice_type') 
                                  if isinstance(results['file2'].get('result'), dict) 
                                  else results['file2'].get('result')),
                'detailed_data': results['file2'].get('detailed_data')
            }
            
            # Generate the system prompt
            system_prompt = generate_system_prompt(doc1_data, doc2_data)
            
            # Use OpenAI to analyze the documents with the system prompt
            # Only keep the AI analysis result, not the system prompt
            ai_analysis = analyze_with_openai(system_prompt, doc1_data, doc2_data)
            results['ai_analysis'] = ai_analysis
            
        # Clean up the results to remove document JSON data
        if results:
            # Create a clean response with only the necessary information
            clean_results = {}
            
            # Keep only minimal file information without detailed data
            if 'file1' in results:
                clean_results['file1'] = {
                    'filename': results['file1'].get('filename'),
                    'type': results['file1'].get('result', {}).get('invoice_type', 'Unknown') 
                           if isinstance(results['file1'].get('result'), dict) 
                           else results['file1'].get('result')
                }
            
            if 'file2' in results:
                clean_results['file2'] = {
                    'filename': results['file2'].get('filename'),
                    'type': results['file2'].get('result', {}).get('invoice_type', 'Unknown') 
                           if isinstance(results['file2'].get('result'), dict) 
                           else results['file2'].get('result')
                }
            
            # Include only the AI analysis results
            if 'ai_analysis' in results:
                clean_results['ai_analysis'] = results['ai_analysis']
            
            return jsonify(clean_results)
        else:
            return jsonify({'error': 'No files were uploaded'})
    
    return render_template('index.html')