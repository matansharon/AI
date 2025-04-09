from typing import Optional, Dict, Any, List
import os
import PyPDF2
import json
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
    
client = OpenAI(api_key=api_key)

# Data Models
class JabilInvoice(BaseModel):
    Part_Name_Description: str = Field(..., description="Part Name / Description")
    Jabil_Part: str = Field(..., description="Jabil Part")
    Jabil_Lot: str = Field(..., description="Jabil Lot")
    Press: str = Field(..., description="Press #")
    Mold: str = Field(..., description="Mold #")
    Date_of_Manufacture: str = Field(..., description="Date of Manufacture")
    Ship_Date: str = Field(..., description="Ship Date")
    Box_Qty: int = Field(..., description="Box Qty")
    Purchasing_Specification: str = Field(..., description="Purchasing Specification #")
    Purchasing_Specification_Rev: str = Field(..., description="Purchasing Specification Rev.")
    Customer_PO: str = Field(..., description="Customer PO")
    Qty_Released: int = Field(..., description="Qty Released")
    Order_Qty_Shipped: int = Field(..., description="Order Qty Shipped")
    Elcam_Drawing: str = Field(..., description="Elcam Drawing #")
    Elcam_Drawing_Rev: str = Field(..., description="Elcam Drawing Rev")
    Elcam_Part: str = Field(..., description="Elcam Part #")
    Abbvie_Part: str = Field(..., description="Abbvie Part #")
    Expiration_Date: str = Field(..., description="Expiration Date")
    Tailgate_Qty_Sent: int = Field(..., description="Tailgate Qty Sent For This Shipment")

class ElcamInvoice(BaseModel):
    Elcam_Part: Optional[str] = Field(None, description="Elcam's Part #")
    AbbVie_Part: Optional[str] = Field(None, description="AbbVie Part #")
    Specs_Number_Rev: Optional[str] = Field(None, description="Specs # and Rev.")
    Part_Name: Optional[str] = Field(None, description="Part Name")
    Batch_Number: Optional[str] = Field(None, description="Batch #")
    Manufacture_Date: Optional[str] = Field(None, description="Manufacture Date")
    Expiry_Date: Optional[str] = Field(None, description="Expiry Date")
    Quantity: Optional[int] = Field(None, description="Quantity")
    PO_Number: Optional[str] = Field(None, description="PO #")
    Tailgate_Samples_Quantity: Optional[int] = Field(None, description="Tailgate samples Quantity")

class TypeInvoice(BaseModel):
    invoice_type: str = Field(..., description="Type of the invoice (Jabil or Elcam)")
    
class ComparisonResult(BaseModel):
    """Model for storing comparison results between documents"""
    matching_fields: List[Dict[str, Any]] = Field(default_factory=list, description="Fields that match between documents")
    mismatched_fields: List[Dict[str, Any]] = Field(default_factory=list, description="Fields that don't match between documents")
    unique_fields: List[Dict[str, Any]] = Field(default_factory=list, description="Fields that exist only in one document")
    overall_match: bool = Field(False, description="Whether all expected matching fields actually match")

# PDF Processing Functions
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

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file
    """
    try:
        reader = PyPDF2.PdfReader(file_path)
        num_pages = len(reader.pages)
        text = ""
        
        # Extract text from all pages
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()
            
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""

# Document Type Detection
def jabil_or_elcam_invoice(file_path: str):
    """
    Determines if the invoice is from Jabil or Elcam based on the file content.

    Args:
        file_path (str): Path to the invoice file.

    Returns:
        dict: JSON result with invoice_type field
    """
    try:
        print(f"Processing file: {file_path}")
        
        # Upload file to OpenAI
        with open(file_path, "rb") as file_data:
            file = client.files.create(
                file=file_data,
                purpose="user_data"
            )
        print(f"File uploaded with ID: {file.id}")

        # Make the API call
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are a helpful assistant. your job is to determine if the invoice is from Jabil or Elcam based on the file content."
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file": {
                                "file_id": file.id,
                            }
                        }
                    ]
                }
            ],
            response_format=TypeInvoice,
        )
        
        # Clean up the file
        try:
            client.files.delete(file.id)
            print(f"File {file.id} deleted.")
        except Exception as delete_error:
            print(f"Error deleting file: {str(delete_error)}")
        
        # Get and return the result
        result = completion.choices[0].message.content
        print(f"Result: {result}")
        
        if hasattr(result, 'model_dump'):
            # Convert pydantic model to dict if needed
            return result.model_dump()
        return result
    
    except Exception as e:
        print(f"Error in jabil_or_elcam_invoice: {str(e)}")
        return {"error": str(e)}

# Legacy function for backward compatibility
def detect_document_type(file_path):
    """Legacy function that calls jabil_or_elcam_invoice"""
    try:
        result = jabil_or_elcam_invoice(file_path)
        if isinstance(result, dict) and 'invoice_type' in result:
            return result['invoice_type']
        return "Unknown"
    except Exception:
        return "Unknown"

# Data Extraction Functions
def extract_jabil_data(file_path):
    """
    Extract data from a Jabil invoice using OpenAI
    
    Args:
        file_path (str): Path to the Jabil invoice file
        
    Returns:
        dict: Extracted data or error message
    """
    file_id = None
    try:
        # Upload file to OpenAI
        with open(file_path, "rb") as file_data:
            file = client.files.create(
                file=file_data,
                purpose="assistants"  # Using assistants purpose
            )
            file_id = file.id
            
        # Make API call to extract data
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that extracts information from Jabil invoices. Format your response as JSON."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract these fields from the Jabil invoice: Part_Name_Description, Jabil_Part, Jabil_Lot, Press, Mold, Date_of_Manufacture, Ship_Date, Box_Qty, Purchasing_Specification, Purchasing_Specification_Rev, Customer_PO, Qty_Released, Order_Qty_Shipped, Elcam_Drawing, Elcam_Drawing_Rev, Elcam_Part, Abbvie_Part, Expiration_Date, and Tailgate_Qty_Sent. Return data as JSON."
                        },
                        {
                            "type": "file_path",
                            "file_path": file_id
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        response_text = completion.choices[0].message.content
        data = json.loads(response_text)
        return data
        
    except Exception as e:
        print(f"Error extracting Jabil data: {str(e)}")
        return {"error": f"Failed to extract data: {str(e)}"}
    finally:
        # Clean up file from OpenAI
        if file_id:
            try:
                client.files.delete(file_id)
            except Exception as cleanup_error:
                print(f"Error cleaning up file: {str(cleanup_error)}")

def extract_elcam_data(file_path):
    """
    Extract data from an Elcam invoice using OpenAI
    
    Args:
        file_path (str): Path to the Elcam invoice file
        
    Returns:
        dict: Extracted data or error message
    """
    file_id = None
    try:
        # Upload file to OpenAI
        with open(file_path, "rb") as file_data:
            file = client.files.create(
                file=file_data,
                purpose="assistants"  # Using assistants purpose
            )
            file_id = file.id
            
        # Make API call to extract data
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that extracts information from Elcam invoices. Format your response as JSON."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract these fields from the Elcam invoice: Elcam_Part, AbbVie_Part, Specs_Number_Rev, Part_Name, Batch_Number, Manufacture_Date, Expiry_Date, Quantity, PO_Number, and Tailgate_Samples_Quantity. Return data as JSON."
                        },
                        {
                            "type": "file_path",
                            "file_path": file_id
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        response_text = completion.choices[0].message.content
        data = json.loads(response_text)
        return data
        
    except Exception as e:
        print(f"Error extracting Elcam data: {str(e)}")
        return {"error": f"Failed to extract data: {str(e)}"}
    finally:
        # Clean up file from OpenAI
        if file_id:
            try:
                client.files.delete(file_id)
            except Exception as cleanup_error:
                print(f"Error cleaning up file: {str(cleanup_error)}")

# Comparison Function
def compare_documents(jabil_data, elcam_data):
    """
    Compare data between Jabil and Elcam documents
    
    Args:
        jabil_data (dict): Data from Jabil document
        elcam_data (dict): Data from Elcam document
        
    Returns:
        dict: Comparison results
    """
    if 'error' in jabil_data or 'error' in elcam_data:
        return {"error": "Cannot compare documents with errors"}
    
    result = ComparisonResult()
    
    # Field mapping between Jabil and Elcam documents
    field_mappings = {
        "Elcam_Part": "Elcam_Part",  # Jabil field : Elcam field
        "Abbvie_Part": "AbbVie_Part",
        "Part_Name_Description": "Part_Name",
        "Purchasing_Specification": "Specs_Number_Rev",
        "Jabil_Lot": "Batch_Number",
        "Date_of_Manufacture": "Manufacture_Date",
        "Expiration_Date": "Expiry_Date",
        "Box_Qty": "Quantity",
        "Customer_PO": "PO_Number",
        "Tailgate_Qty_Sent": "Tailgate_Samples_Quantity"
    }
    
    # Check each mapping
    for jabil_field, elcam_field in field_mappings.items():
        jabil_value = jabil_data.get(jabil_field)
        elcam_value = elcam_data.get(elcam_field)
        
        if jabil_value and elcam_value:
            # Both fields exist
            jabil_str = str(jabil_value).strip().lower()
            elcam_str = str(elcam_value).strip().lower()
            
            if jabil_str == elcam_str:
                result.matching_fields.append({
                    "jabil_field": jabil_field,
                    "elcam_field": elcam_field,
                    "value": jabil_value
                })
            else:
                result.mismatched_fields.append({
                    "jabil_field": jabil_field,
                    "jabil_value": jabil_value,
                    "elcam_field": elcam_field,
                    "elcam_value": elcam_value
                })
        elif jabil_value:
            # Only Jabil has a value
            result.unique_fields.append({
                "document": "Jabil",
                "field": jabil_field,
                "value": jabil_value
            })
        elif elcam_value:
            # Only Elcam has a value
            result.unique_fields.append({
                "document": "Elcam",
                "field": elcam_field,
                "value": elcam_value
            })
    
    # Check if all expected matching fields actually match
    result.overall_match = len(result.mismatched_fields) == 0
    
    return result.model_dump()