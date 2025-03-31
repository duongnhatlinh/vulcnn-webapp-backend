from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import os
import json
import requests
from datetime import datetime
from werkzeug.utils import secure_filename
from app import db
from models.scan import Scan
from models.project import Project
from models.file import File
from models.pdg import PDG
from models.report import Report
from models.vulnerability import Vulnerability
from services.scan_service import process_scan

scans_bp = Blueprint('scans', __name__)

@scans_bp.route('', methods=['GET'])
@jwt_required()
def get_scans():
    current_user_id = get_jwt_identity()
    
    scans = Scan.query.filter_by(user_id=current_user_id).order_by(Scan.started_at.desc()).all()
    
    result = []
    for scan in scans:
        scan_data = scan.to_dict()
        
        # Add project info
        project = Project.query.get(scan.project_id)
        if project:
            scan_data['project'] = {
                'id': project.id,
                'name': project.name
            }
        
        result.append(scan_data)
    
    return jsonify(result), 200

@scans_bp.route('/<scan_id>', methods=['GET'])
@jwt_required()
def get_scan(scan_id):
    current_user_id = get_jwt_identity()
    
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user_id).first()
    
    if not scan:
        return jsonify({'message': 'Scan not found'}), 404
    
    scan_data = scan.to_dict()
    
    # Add project info
    project = Project.query.get(scan.project_id)
    if project:
        scan_data['project'] = {
            'id': project.id,
            'name': project.name
        }
    
    # Add files info
    files = db.session.query(File).join(Vulnerability).filter(
        Vulnerability.scan_id == scan_id,
        Vulnerability.file_id == File.id
    ).distinct().all()
    
    scan_data['files'] = [file.to_dict() for file in files]
    
    return jsonify(scan_data), 200

@scans_bp.route('', methods=['POST'])
@jwt_required()
def create_scan():
    current_user_id = get_jwt_identity()
    
    # Check if multipart form data
    if 'files[]' not in request.files and 'file' not in request.files:
        return jsonify({'message': 'No files provided'}), 400
    
    project_id = request.form.get('project_id')
    
    # Validate project
    if project_id:
        project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
        if not project:
            return jsonify({'message': 'Project not found'}), 404
    else:
        # Create a default project for the scan
        project_id = str(uuid.uuid4())
        default_project = Project(
            id=project_id,
            user_id=current_user_id,
            name=f"Scan {datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')}",
            description="Auto-created project for scan"
        )
        db.session.add(default_project)
        db.session.commit()
    
    # Parse scan options
    scan_options = {}
    if 'options' in request.form:
        try:
            scan_options = json.loads(request.form['options'])
        except:
            pass
    
    # Create scan record
    scan_id = str(uuid.uuid4())
    new_scan = Scan(
        id=scan_id,
        project_id=project_id,
        user_id=current_user_id,
        scan_options=scan_options
    )
    
    db.session.add(new_scan)
    db.session.commit()
    
    # Process uploaded files
    uploaded_files = []
    files = request.files.getlist('files[]') if 'files[]' in request.files else [request.files['file']]
    
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], scan_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        if file.filename == '':
            continue
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Create file record
        file_id = str(uuid.uuid4())
        file_record = File(
            id=file_id,
            project_id=project_id,
            filename=filename,
            file_path=file_path,
            content_type=file.content_type,
            file_size=os.path.getsize(file_path)
        )
        
        db.session.add(file_record)
        uploaded_files.append(file_record)
    
    db.session.commit()
    
    # Start scan processing in background
    process_scan.delay(scan_id, [f.id for f in uploaded_files])
    
    return jsonify({
        'message': 'Scan created and processing started',
        'scan': new_scan.to_dict(),
        'files': [file.to_dict() for file in uploaded_files]
    }), 201

@scans_bp.route('/<scan_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_scan(scan_id):
    current_user_id = get_jwt_identity()
    
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user_id).first()
    
    if not scan:
        return jsonify({'message': 'Scan not found'}), 404
    
    if scan.status not in ['pending', 'processing']:
        return jsonify({'message': 'Scan cannot be cancelled anymore'}), 400
    
    scan.status = 'cancelled'
    scan.completed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Scan cancelled successfully',
        'scan': scan.to_dict()
    }), 200

@scans_bp.route('/<scan_id>/results', methods=['GET'])
@jwt_required()
def get_scan_results(scan_id):
    current_user_id = get_jwt_identity()
    
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user_id).first()
    
    if not scan:
        return jsonify({'message': 'Scan not found'}), 404
    
    # Get vulnerabilities
    vulnerabilities = Vulnerability.query.filter_by(scan_id=scan_id).all()
    
    # Organize by file
    results = {}
    for vuln in vulnerabilities:
        file = File.query.get(vuln.file_id)
        if not file:
            continue
        
        if file.id not in results:
            results[file.id] = {
                'file': file.to_dict(),
                'vulnerabilities': []
            }
        
        results[file.id]['vulnerabilities'].append(vuln.to_dict())
    
    return jsonify({
        'scan': scan.to_dict(),
        'results': list(results.values())
    }), 200

@scans_bp.route('/<scan_id>/pdg/<file_id>', methods=['GET'])
@jwt_required()
def get_scan_pdg(scan_id, file_id):
    current_user_id = get_jwt_identity()
    
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user_id).first()
    
    if not scan:
        return jsonify({'message': 'Scan not found'}), 404
    
    file = File.query.filter_by(id=file_id, project_id=scan.project_id).first()
    
    if not file:
        return jsonify({'message': 'File not found'}), 404
    
    # Get PDG from database
    pdg = db.session.query(PDG).filter_by(scan_id=scan_id, file_id=file_id).first()
    
    if not pdg:
        return jsonify({'message': 'PDG not found for this file'}), 404
    
    return jsonify(pdg.to_dict()), 200

@scans_bp.route('/<scan_id>/report', methods=['GET'])
@jwt_required()
def generate_scan_report(scan_id):
    current_user_id = get_jwt_identity()
    
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user_id).first()
    
    if not scan:
        return jsonify({'message': 'Scan not found'}), 404
    
    # Get report format
    report_format = request.args.get('format', 'pdf')
    
    # Request report from results service
    results_service_url = current_app.config['RESULTS_SERVICE_URL']
    response = requests.get(
        f"{results_service_url}/generate_report/{scan_id}",
        params={'format': report_format}
    )
    
    if response.status_code != 200:
        return jsonify({'message': 'Failed to generate report'}), 500
    
    # Create report record
    report_id = str(uuid.uuid4())
    report_path = response.json().get('report_path')
    
    new_report = Report(
        id=report_id,
        scan_id=scan_id,
        user_id=current_user_id,
        report_type=report_format,
        file_path=report_path
    )
    
    db.session.add(new_report)
    db.session.commit()
    
    # Return report URL or file
    if report_format == 'json':
        return jsonify(response.json().get('report_data')), 200
    else:
        return jsonify({
            'message': 'Report generated successfully',
            'report_id': report_id,
            'download_url': f"/api/reports/{report_id}/download"
        }), 200