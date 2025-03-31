from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import os
import requests
from app import db
from models.report import Report
from models.scan import Scan

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('', methods=['GET'])
@jwt_required()
def get_reports():
    current_user_id = get_jwt_identity()
    
    reports = Report.query.filter_by(user_id=current_user_id).all()
    
    return jsonify([report.to_dict() for report in reports]), 200

@reports_bp.route('/<report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    current_user_id = get_jwt_identity()
    
    report = Report.query.filter_by(id=report_id, user_id=current_user_id).first()
    
    if not report:
        return jsonify({'message': 'Report not found'}), 404
    
    return jsonify(report.to_dict()), 200

@reports_bp.route('', methods=['POST'])
@jwt_required()
def create_report():
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('scan_id'):
        return jsonify({'message': 'Missing scan ID'}), 400
    
    scan_id = data['scan_id']
    
    # Verify scan exists and belongs to user
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user_id).first()
    if not scan:
        return jsonify({'message': 'Scan not found'}), 404
    
    # Get report format
    report_format = data.get('format', 'pdf')
    
    # Get report options
    report_options = data.get('options', {})
    
    # Request report from results service
    results_service_url = current_app.config['RESULTS_SERVICE_URL']
    response = requests.post(
        f"{results_service_url}/generate_report",
        json={
            'scan_id': scan_id,
            'format': report_format,
            'options': report_options
        }
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
        file_path=report_path,
        report_options=report_options
    )
    
    db.session.add(new_report)
    db.session.commit()
    
    return jsonify({
        'message': 'Report generated successfully',
        'report': new_report.to_dict()
    }), 201

@reports_bp.route('/<report_id>/download', methods=['GET'])
@jwt_required()
def download_report(report_id):
    current_user_id = get_jwt_identity()
    
    report = Report.query.filter_by(id=report_id, user_id=current_user_id).first()
    
    if not report:
        return jsonify({'message': 'Report not found'}), 404
    
    # Check if file exists
    file_path = report.file_path
    if not os.path.exists(file_path):
        return jsonify({'message': 'Report file not found'}), 404
    
    # Determine MIME type based on report type
    mimetype = 'application/octet-stream'
    if report.report_type == 'pdf':
        mimetype = 'application/pdf'
    elif report.report_type == 'csv':
        mimetype = 'text/csv'
    elif report.report_type == 'html':
        mimetype = 'text/html'
    elif report.report_type == 'json':
        mimetype = 'application/json'
    
    # Return file
    return send_file(
        file_path,
        mimetype=mimetype,
        as_attachment=True,
        download_name=f"report_{report.id}.{report.report_type}"
    )

@reports_bp.route('/<report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    current_user_id = get_jwt_identity()
    
    report = Report.query.filter_by(id=report_id, user_id=current_user_id).first()
    
    if not report:
        return jsonify({'message': 'Report not found'}), 404
    
    # Delete file from disk
    file_path = report.file_path
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            # Log error but continue
            print(f"Error deleting report file: {str(e)}")
    
    # Delete from database
    db.session.delete(report)
    db.session.commit()
    
    return jsonify({'message': 'Report deleted successfully'}), 200