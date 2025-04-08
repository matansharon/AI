from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import os
from openai import OpenAI
import json
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
    
client = OpenAI(api_key=api_key)

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



def jabil_or_elcam_invoice(file_path: str) -> Dict:
    """
    Determines if the invoice is from Jabil or Elcam based on the file content.

    Args:
        file_path (str): Path to the invoice file.

    Returns:
        Dict: Dictionary with invoice_type field.
    """
    # Here you can implement logic to determine the invoice type based on its content
    # For now, let's assume we are just checking the filename for simplicity
    
    try:
        with open(file_path, "rb") as file_data:
            file = client.files.create(
                file=file_data,
                purpose="user_data"
            )
        
        # Print debug info before making API call
        print(f"Making API call to determine document type for: {file_path}")
        
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
        
        # Print debug info after API call
        print(f"API call completed")
        
        # Clean up the file from OpenAI
        client.files.delete(file.id)
        
        # Get the content and add debug info
        result = completion.choices[0].message.content
        print(f"API result content: {result}")
        print(f"API result type: {type(result)}")
        
        # Try to handle different possible result formats
        if hasattr(result, 'invoice_type'):
            print(f"Found invoice_type attribute: {result.invoice_type}")
            return {"invoice_type": result.invoice_type}
            
        # Default - return the original result
        return result
    
    except Exception as e:
        # In case of error, return an error message
        print(f"Error in jabil_or_elcam_invoice: {str(e)}")
        # For demo purposes, return the mock data if API calls fail
        return {"invoice_type": "Jabil" if "jabil" in file_path.lower() else "Elcam"}

def exctract_invoice_data_form_jabil_invoice(file_path: str) -> Dict:
    """
    Extracts data from a Jabil invoice.

    Args:
        file_path (str): Path to the Jabil invoice file.

    Returns:
        Dict: Dictionary containing the extracted fields or error message
    """
    try:
        print(f"Extracting Jabil invoice data from: {file_path}")
        # Upload file to OpenAI with proper file handling
        with open(file_path, "rb") as file_data:
            file = client.files.create(
                file=file_data,
                purpose="user_data"
            )
        print(f"File uploaded with ID: {file.id}")
        
        print("Starting Jabil data extraction API call")
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are a helpful assistant that can extract information from invoices. You will be provided with an invoice file and a question about the invoice. Please answer the question based on the information in the invoice."
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
                        },
                        {
                            "type": "text",
                            "text": "Extract all fields from this Jabil invoice including Part Name/Description, Jabil Part, Jabil Lot, Press #, Mold #, Date of Manufacture, Ship Date, Box Qty, Purchasing Specification #, Purchasing Specification Rev., Customer PO, Qty Released, Order Qty Shipped, Elcam Drawing #, Elcam Drawing Rev, Elcam Part #, Abbvie Part #, Expiration Date, and Tailgate Qty Sent."
                        }
                    ]
                }
            ],
            response_format=JabilInvoice,
        )
        print("Jabil API call completed")
        
        # Clean up the file from OpenAI
        client.files.delete(file.id)
        
        # Get the content and add debug info
        result = completion.choices[0].message.content
        print(f"Jabil extraction result type: {type(result)}")
        
        if hasattr(result, 'model_dump'):
            # If it has model_dump method, use it
            data = result.model_dump()
            print(f"Jabil data after model_dump: {data}")
            return data
        elif isinstance(result, dict):
            # If it's already a dictionary
            print(f"Jabil data (already dict): {result}")
            return result
        else:
            # If it's something else, return an error
            print(f"Unexpected result type: {type(result)}")
            return {"error": f"Unexpected result type: {type(result)}"}
    
    except Exception as e:
        # In case of error, return an error message
        print(f"Error in extract_jabil_invoice_data: {str(e)}")
        # For demo purposes, return mock data if API calls fail
        return {"error": f"Failed to extract Jabil invoice data: {str(e)}"}
        

def extract_elcam_invoice_data(file_path: str) -> Dict:
    """
    Extracts data from an Elcam invoice.

    Args:
        file_path (str): Path to the Elcam invoice file.

    Returns:
        Dict: Dictionary containing the extracted fields or error message
    """
    try:
        print(f"Extracting Elcam invoice data from: {file_path}")
        # Upload file to OpenAI with proper file handling
        with open(file_path, "rb") as file_data:
            file = client.files.create(
                file=file_data,
                purpose="user_data"
            )
        print(f"File uploaded with ID: {file.id}")
        
        # Using similar approach to Jabil but with Elcam fields
        print("Starting Elcam data extraction API call")
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are a helpful assistant that can extract information from invoices. You will be provided with an invoice file and a question about the invoice. Please answer the question based on the information in the invoice."
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
                        },
                        {
                            "type": "text",
                            "text": "Extract all fields from this Elcam invoice: Elcam's Part #, AbbVie Part #, Specs # and Rev., Part Name, Batch #, Manufacture Date, Expiry Date, Quantity, PO #, and Tailgate samples Quantity."
                        }
                    ]
                }
            ],
            response_format=ElcamInvoice,
        )
        print("Elcam API call completed")
        
        # Clean up the file from OpenAI
        client.files.delete(file.id)
        
        # Get the content and add debug info
        result = completion.choices[0].message.content
        print(f"Elcam extraction result type: {type(result)}")
        
        if hasattr(result, 'model_dump'):
            # If it has model_dump method, use it
            data = result.model_dump()
            print(f"Elcam data after model_dump: {data}")
            return data
        elif isinstance(result, dict):
            # If it's already a dictionary
            print(f"Elcam data (already dict): {result}")
            return result
        else:
            # If it's something else, return an error
            print(f"Unexpected result type: {type(result)}")
            return {"error": f"Unexpected result type: {type(result)}"}
    
    except Exception as e:
        # In case of error, return an error message
        print(f"Error in extract_elcam_invoice_data: {str(e)}")
        # For demo purposes, return error message
        return {"error": f"Failed to extract Elcam invoice data: {str(e)}"}
        
def compare_documents(jabil_data: Dict, elcam_data: Dict) -> Dict:
    """
    Compare data between Jabil and Elcam invoices.
    
    Args:
        jabil_data: Dictionary with Jabil invoice data
        elcam_data: Dictionary with Elcam invoice data
        
    Returns:
        Dictionary with comparison results
    """
    if 'error' in jabil_data or 'error' in elcam_data:
        return {"error": "Cannot compare documents with errors"}
    
    result = ComparisonResult()
    
    # Field mapping between Jabil and Elcam documents
    field_mappings = {
        "Elcam_Part": "Elcam_Part",  # Jabil field : Elcam field
        "Abbvie_Part": "AbbVie_Part",
        "Part_Name_Description": "Part_Name",
        "Purchasing_Specification": "Specs_Number_Rev",  # This is an approximation
        "Jabil_Lot": "Batch_Number",
        "Date_of_Manufacture": "Manufacture_Date",
        "Expiration_Date": "Expiry_Date",
        "Box_Qty": "Quantity",
        "Customer_PO": "PO_Number",
        "Tailgate_Qty_Sent": "Tailgate_Samples_Quantity"
    }
    
    # Check each mapping
    for jabil_field, elcam_field in field_mappings.items():
        if jabil_field in jabil_data and elcam_field in elcam_data:
            # Both fields exist
            jabil_value = jabil_data.get(jabil_field)
            elcam_value = elcam_data.get(elcam_field)
            
            if jabil_value and elcam_value:
                # Convert to strings for comparison if needed
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
        elif jabil_field in jabil_data:
            # Only Jabil has this field
            result.unique_fields.append({
                "document": "Jabil",
                "field": jabil_field,
                "value": jabil_data.get(jabil_field)
            })
        elif elcam_field in elcam_data:
            # Only Elcam has this field
            result.unique_fields.append({
                "document": "Elcam",
                "field": elcam_field,
                "value": elcam_data.get(elcam_field)
            })
    
    # Check if all expected matching fields actually match
    result.overall_match = len(result.mismatched_fields) == 0
    
    return result.model_dump()

