from app import db
from celery import Celery
from models.scan import Scan
from models.file import File
from models.vulnerability import Vulnerability
from models.pdg import PDG
import os
import uuid
import requests
import json
from datetime import datetime
import config

# Initialize Celery
celery = Celery('scan_service')
celery.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

@celery.task
def process_scan(scan_id, file_ids):
    """
    Process a scan in the background using a task queue.
    
    Args:
        scan_id: The ID of the scan to process
        file_ids: List of file IDs to include in the scan
    """
    try:
        # Update scan status
        scan = Scan.query.get(scan_id)
        if not scan:
            return {"error": "Scan not found"}
        
        scan.status = "processing"
        db.session.commit()
        
        # Process each file
        for file_id in file_ids:
            file = File.query.get(file_id)
            if not file:
                continue
            
            # Step 1: Normalize code
            normalized_file_path = normalize_code(file.file_path)
            if not normalized_file_path:
                continue
            
            # Step 2: Generate PDG
            pdg_file_path = generate_pdg(normalized_file_path)
            if not pdg_file_path:
                continue
            
            # Step 3: Generate image representation
            image_file_path = generate_image(pdg_file_path)
            if not image_file_path:
                continue
            
            # Step 4: Run vulnerability prediction
            vulnerabilities = predict_vulnerabilities(image_file_path, file.id)
            if not vulnerabilities:
                continue
            
            # Save PDG to database
            with open(pdg_file_path, 'r') as f:
                pdg_data = f.read()
            
            pdg_id = str(uuid.uuid4())
            pdg = PDG(
                id=pdg_id,
                file_id=file.id,
                scan_id=scan_id,
                pdg_data=pdg_data
            )
            db.session.add(pdg)
            
            # Save vulnerabilities to database
            for vuln in vulnerabilities:
                vuln_id = str(uuid.uuid4())
                vulnerability = Vulnerability(
                    id=vuln_id,
                    scan_id=scan_id,
                    file_id=file.id,
                    function_name=vuln.get('function_name'),
                    line_number=vuln.get('line_number'),
                    severity=vuln.get('severity'),
                    vulnerability_type=vuln.get('type'),
                    cwe_id=vuln.get('cwe_id'),
                    description=vuln.get('description'),
                    code_snippet=vuln.get('code_snippet'),
                    recommendation=vuln.get('recommendation'),
                    confidence_score=vuln.get('confidence_score')
                )
                db.session.add(vulnerability)
                
                # Update scan counts
                scan.vulnerabilities_count += 1
                if vuln.get('severity') == 'high':
                    scan.high_severity_count += 1
                elif vuln.get('severity') == 'medium':
                    scan.medium_severity_count += 1
                elif vuln.get('severity') == 'low':
                    scan.low_severity_count += 1
        
        # Update scan status
        scan.status = "completed"
        scan.completed_at = datetime.utcnow()
        db.session.commit()
        
        return {"status": "success", "scan_id": scan_id}
    
    except Exception as e:
        # Log error and update scan status
        print(f"Error processing scan {scan_id}: {str(e)}")
        
        scan = Scan.query.get(scan_id)
        if scan:
            scan.status = "failed"
            scan.completed_at = datetime.utcnow()
            db.session.commit()
        
        return {"error": str(e)}

def normalize_code(file_path):
    """Normalize code by calling the normalization service"""
    try:
        normalized_dir = os.path.join(config.UPLOAD_FOLDER, '../normalized')
        os.makedirs(normalized_dir, exist_ok=True)
        
        filename = os.path.basename(file_path)
        normalized_path = os.path.join(normalized_dir, filename)
        
        # Call normalization service
        response = requests.post(
            f"{config.NORMALIZATION_SERVICE_URL}/normalize",
            files={'file': open(file_path, 'rb')},
            data={'output_path': normalized_path}
        )
        
        if response.status_code != 200:
            print(f"Normalization failed: {response.text}")
            return None
        
        return normalized_path
    except Exception as e:
        print(f"Error in code normalization: {str(e)}")
        return None

def generate_pdg(file_path):
    """Generate PDG from normalized code"""
    try:
        pdg_dir = os.path.join(config.UPLOAD_FOLDER, '../pdgs')
        os.makedirs(pdg_dir, exist_ok=True)
        
        filename = os.path.basename(file_path)
        pdg_path = os.path.join(pdg_dir, f"{filename}.dot")
        
        # Call PDG generator service
        response = requests.post(
            f"{config.PDG_GENERATOR_SERVICE_URL}/generate_pdg",
            files={'file': open(file_path, 'rb')},
            data={'output_path': pdg_path}
        )
        
        if response.status_code != 200:
            print(f"PDG generation failed: {response.text}")
            return None
        
        return pdg_path
    except Exception as e:
        print(f"Error in PDG generation: {str(e)}")
        return None

def generate_image(pdg_path):
    """Generate image representation from PDG"""
    try:
        image_dir = os.path.join(config.UPLOAD_FOLDER, '../images')
        os.makedirs(image_dir, exist_ok=True)
        
        filename = os.path.basename(pdg_path)
        image_path = os.path.join(image_dir, f"{filename}.pkl")
        
        # Call image generator service
        response = requests.post(
            f"{config.IMAGE_GENERATOR_SERVICE_URL}/generate_image",
            files={'pdg_file': open(pdg_path, 'rb')},
            data={'output_path': image_path}
        )
        
        if response.status_code != 200:
            print(f"Image generation failed: {response.text}")
            return None
        
        return image_path
    except Exception as e:
        print(f"Error in image generation: {str(e)}")
        return None

def predict_vulnerabilities(image_path, file_id):
    """Predict vulnerabilities from image representation"""
    try:
        # Call prediction service
        response = requests.post(
            f"{config.PREDICTION_SERVICE_URL}/predict",
            files={'image_file': open(image_path, 'rb')},
            data={'file_id': file_id}
        )
        
        if response.status_code != 200:
            print(f"Vulnerability prediction failed: {response.text}")
            return None
        
        result = response.json()
        return result.get('vulnerabilities', [])
    except Exception as e:
        print(f"Error in vulnerability prediction: {str(e)}")
        return None