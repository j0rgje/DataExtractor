"""
Azure Functions voor documentverwerking
Dit bestand bevat voorbeeldcode voor Azure Functions die gebruikt worden
voor PDF naar tekst conversie en data extractie.
"""

import azure.functions as func
import json
import logging
from azure.storage.blob import BlobServiceClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time
import re
from typing import Dict, List, Any
import io
import PyPDF2

# Azure Function App
app = func.FunctionApp()

# Configuratie (zou uit environment variables komen)
STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;..."
COMPUTER_VISION_ENDPOINT = "https://yourregion.api.cognitive.microsoft.com/"
COMPUTER_VISION_KEY = "your_computer_vision_key"

# Initialize Azure services
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
cv_client = ComputerVisionClient(
    COMPUTER_VISION_ENDPOINT, 
    CognitiveServicesCredentials(COMPUTER_VISION_KEY)
)

@app.route(route="convert_pdf_to_text", auth_level=func.AuthLevel.FUNCTION)
def convert_pdf_to_text(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function om PDF documenten te converteren naar tekst
    
    Input: PDF bestand via HTTP POST
    Output: Geëxtraheerde tekst in JSON formaat
    """
    logging.info('PDF to text conversion function started.')
    
    try:
        # Krijg bestand uit request
        files = req.files.getlist('file')
        if not files:
            return func.HttpResponse(
                json.dumps({"error": "Geen bestand gevonden in request"}),
                status_code=400,
                mimetype="application/json"
            )
        
        file = files[0]
        
        # Valideer bestandstype
        if not file.filename.lower().endswith('.pdf'):
            return func.HttpResponse(
                json.dumps({"error": "Alleen PDF bestanden worden ondersteund"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Lees PDF content
        pdf_content = file.read()
        
        # Optie 1: Gebruik Azure Computer Vision OCR voor gescande PDFs
        extracted_text = extract_text_with_computer_vision(pdf_content)
        
        # Optie 2: Fallback naar PyPDF2 voor tekst-gebaseerde PDFs
        if not extracted_text or len(extracted_text.strip()) < 50:
            extracted_text = extract_text_with_pypdf2(pdf_content)
        
        # Sla resultaat op in Blob Storage
        blob_name = f"extracted_text/{file.filename}_{int(time.time())}.txt"
        upload_text_to_blob(extracted_text, blob_name)
        
        result = {
            "success": True,
            "text": extracted_text,
            "blob_url": f"https://yourstorageaccount.blob.core.windows.net/documents/{blob_name}",
            "processing_time": time.time()
        }
        
        logging.info(f'PDF conversion completed successfully. Text length: {len(extracted_text)}')
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f'Error in PDF conversion: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": f"Fout bij conversie: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="extract_purchase_order_data", auth_level=func.AuthLevel.FUNCTION)
def extract_purchase_order_data(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function om gestructureerde data te extraheren uit inkooporder tekst
    
    Input: Tekst van geconverteerde PDF
    Output: Gestructureerde data in JSON formaat
    """
    logging.info('Purchase order data extraction function started.')
    
    try:
        # Krijg tekst uit request
        req_body = req.get_json()
        if not req_body or 'text' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Geen tekst gevonden in request"}),
                status_code=400,
                mimetype="application/json"
            )
        
        text = req_body['text']
        
        # Extract structured data using regex patterns and AI
        extracted_data = extract_structured_data(text)
        
        # Valideer en enrichment data
        validated_data = validate_and_enrich_data(extracted_data)
        
        # Sla resultaat op in Blob Storage
        blob_name = f"extracted_data/order_{int(time.time())}.json"
        upload_json_to_blob(validated_data, blob_name)
        
        result = {
            "success": True,
            "extracted_data": validated_data,
            "blob_url": f"https://yourstorageaccount.blob.core.windows.net/documents/{blob_name}",
            "confidence_score": calculate_confidence_score(validated_data)
        }
        
        logging.info('Data extraction completed successfully.')
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f'Error in data extraction: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": f"Fout bij data extractie: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

def extract_text_with_computer_vision(pdf_content: bytes) -> str:
    """Extraheer tekst uit PDF met Azure Computer Vision OCR"""
    try:
        # Upload naar blob voor Computer Vision processing
        blob_name = f"temp/pdf_{int(time.time())}.pdf"
        blob_client = blob_service_client.get_blob_client(
            container="documents", 
            blob=blob_name
        )
        blob_client.upload_blob(pdf_content, overwrite=True)
        
        # Start OCR operatie
        blob_url = blob_client.url
        ocr_operation = cv_client.read(blob_url, raw=True)
        
        # Wacht op voltooiing
        operation_id = ocr_operation.headers["Operation-Location"].split("/")[-1]
        
        while True:
            result = cv_client.get_read_result(operation_id)
            if result.status not in [OperationStatusCodes.not_started, OperationStatusCodes.running]:
                break
            time.sleep(1)
        
        # Extraheer tekst
        extracted_text = ""
        if result.status == OperationStatusCodes.succeeded:
            for text_result in result.analyze_result.read_results:
                for line in text_result.lines:
                    extracted_text += line.text + "\n"
        
        # Cleanup temp blob
        blob_client.delete_blob()
        
        return extracted_text
        
    except Exception as e:
        logging.warning(f'Computer Vision OCR failed: {str(e)}')
        return ""

def extract_text_with_pypdf2(pdf_content: bytes) -> str:
    """Fallback extractie met PyPDF2 voor tekst-gebaseerde PDFs"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        extracted_text = ""
        
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + "\n"
        
        return extracted_text
        
    except Exception as e:
        logging.warning(f'PyPDF2 extraction failed: {str(e)}')
        return ""

def extract_structured_data(text: str) -> Dict[str, Any]:
    """Extraheer gestructureerde data uit tekst met regex patterns"""
    
    data = {
        "order_number": None,
        "date": None,
        "supplier": None,
        "items": [],
        "subtotal": None,
        "vat_rate": None,
        "vat_amount": None,
        "total": None,
        "delivery_address": {}
    }
    
    # Order number pattern
    order_patterns = [
        r"order\s+number[:\s]+([A-Z0-9-]+)",
        r"purchase\s+order[:\s]+([A-Z0-9-]+)",
        r"po[:\s]+([A-Z0-9-]+)"
    ]
    
    for pattern in order_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["order_number"] = match.group(1)
            break
    
    # Date pattern
    date_patterns = [
        r"date[:\s]+(\d{4}-\d{2}-\d{2})",
        r"date[:\s]+(\d{2}/\d{2}/\d{4})",
        r"(\d{2}-\d{2}-\d{4})"
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["date"] = match.group(1)
            break
    
    # Supplier pattern
    supplier_patterns = [
        r"supplier[:\s]+([^\n]+)",
        r"vendor[:\s]+([^\n]+)"
    ]
    
    for pattern in supplier_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["supplier"] = match.group(1).strip()
            break
    
    # Line items pattern
    item_pattern = r"[-*•]\s*([^:]+):\s*(\d+)\s*units?\s*@\s*€?(\d+\.?\d*)\s*=\s*€?(\d+\.?\d*)"
    items = re.findall(item_pattern, text, re.IGNORECASE)
    
    for item in items:
        data["items"].append({
            "product": item[0].strip(),
            "quantity": int(item[1]),
            "unit_price": float(item[2]),
            "total": float(item[3])
        })
    
    # Financial totals
    subtotal_match = re.search(r"subtotal[:\s]+€?(\d+\.?\d*)", text, re.IGNORECASE)
    if subtotal_match:
        data["subtotal"] = float(subtotal_match.group(1))
    
    vat_match = re.search(r"vat\s*\((\d+)%\)[:\s]+€?(\d+\.?\d*)", text, re.IGNORECASE)
    if vat_match:
        data["vat_rate"] = float(vat_match.group(1)) / 100
        data["vat_amount"] = float(vat_match.group(2))
    
    total_match = re.search(r"total[:\s]+€?(\d+\.?\d*)", text, re.IGNORECASE)
    if total_match:
        data["total"] = float(total_match.group(1))
    
    return data

def validate_and_enrich_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valideer en enrichment geëxtraheerde data"""
    
    # Bereken ontbrekende totalen
    if data["items"] and not data["subtotal"]:
        data["subtotal"] = sum(item["total"] for item in data["items"])
    
    if data["subtotal"] and data["vat_rate"] and not data["vat_amount"]:
        data["vat_amount"] = data["subtotal"] * data["vat_rate"]
    
    if data["subtotal"] and data["vat_amount"] and not data["total"]:
        data["total"] = data["subtotal"] + data["vat_amount"]
    
    # Voeg metadata toe
    data["validation"] = {
        "has_order_number": bool(data["order_number"]),
        "has_date": bool(data["date"]),
        "has_supplier": bool(data["supplier"]),
        "has_items": len(data["items"]) > 0,
        "totals_match": abs((data["subtotal"] or 0) + (data["vat_amount"] or 0) - (data["total"] or 0)) < 0.01
    }
    
    return data

def calculate_confidence_score(data: Dict[str, Any]) -> float:
    """Bereken confidence score voor geëxtraheerde data"""
    
    validation = data.get("validation", {})
    score = 0.0
    
    if validation.get("has_order_number"):
        score += 0.25
    if validation.get("has_date"):
        score += 0.15
    if validation.get("has_supplier"):
        score += 0.20
    if validation.get("has_items"):
        score += 0.25
    if validation.get("totals_match"):
        score += 0.15
    
    return round(score, 2)

def upload_text_to_blob(text: str, blob_name: str):
    """Upload tekst naar Azure Blob Storage"""
    try:
        blob_client = blob_service_client.get_blob_client(
            container="documents", 
            blob=blob_name
        )
        blob_client.upload_blob(text, overwrite=True)
    except Exception as e:
        logging.error(f'Failed to upload text to blob: {str(e)}')

def upload_json_to_blob(data: Dict[str, Any], blob_name: str):
    """Upload JSON data naar Azure Blob Storage"""
    try:
        blob_client = blob_service_client.get_blob_client(
            container="documents", 
            blob=blob_name
        )
        json_content = json.dumps(data, indent=2)
        blob_client.upload_blob(json_content, overwrite=True)
    except Exception as e:
        logging.error(f'Failed to upload JSON to blob: {str(e)}')

# Timer-triggered function voor cleanup van oude bestanden
@app.timer_trigger(schedule="0 0 2 * * *", arg_name="timer", run_on_startup=False)
def cleanup_old_files(timer: func.TimerRequest) -> None:
    """Dagelijkse cleanup van oude temporary bestanden"""
    logging.info('Starting cleanup of old files.')
    
    try:
        # Cleanup temp files ouder dan 24 uur
        container_client = blob_service_client.get_container_client("documents")
        
        for blob in container_client.list_blobs(name_starts_with="temp/"):
            # Check of blob ouder is dan 24 uur
            if blob.last_modified < (datetime.utcnow() - timedelta(days=1)):
                container_client.delete_blob(blob.name)
                logging.info(f'Deleted old temp file: {blob.name}')
                
    except Exception as e:
        logging.error(f'Error during cleanup: {str(e)}')
