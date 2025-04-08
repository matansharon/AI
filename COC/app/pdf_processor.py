import PyPDF2
import os

def validate_pdf(file):
    """
    Validate if the uploaded file is a PDF
    """
    try:
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            return False
            
        # Try to read it as a PDF
        reader = PyPDF2.PdfReader(file)
        # If we get here, it's a valid PDF
        file.seek(0)  # Reset file pointer for later use
        return True
    except Exception as e:
        print(f"PDF validation error: {str(e)}")
        return False

def extract_pdf_fields(file_path):
    """
    Extract fields from PDF file
    Returns a dictionary of extracted fields
    """
    try:
        reader = PyPDF2.PdfReader(file_path)
        num_pages = len(reader.pages)
        text = ""
        
        # Extract text from all pages
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()
            
        # For now, just return basic info about the PDF
        # You would implement your specific field extraction logic here
        extracted_data = {
            'filename': os.path.basename(file_path),
            'pages': num_pages,
            'text_sample': text[:200] + '...' if len(text) > 200 else text
            # Add more extracted fields here based on your requirements
        }
        
        return extracted_data
    except Exception as e:
        print(f"Error extracting PDF fields: {str(e)}")
        return {'error': str(e)}
