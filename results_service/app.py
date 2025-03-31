from flask import Flask, request, jsonify, send_file
import os
import tempfile
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Import results processing modules
from processor.vulnerability_processor import process_vulnerabilities
from processor.report_generator import generate_report

@app.route('/generate_report', methods=['POST'])
def create_report():
    """
    Generate a report from scan results
    
    POST parameters (JSON):
    - scan_id: ID of the scan
    - format: Report format (pdf, csv, html, json)
    - options: Additional report options
    """
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('scan_id'):
        return jsonify({'error': 'Missing scan ID'}), 400
    
    scan_id = data['scan_id']
    report_format = data.get('format', 'pdf')
    report_options = data.get('options', {})
    
    try:
        # Process vulnerabilities
        vulnerabilities = process_vulnerabilities(scan_id)
        
        # Generate report
        report_path = generate_report(
            scan_id=scan_id,
            vulnerabilities=vulnerabilities,
            report_format=report_format,
            options=report_options
        )
        
        if not report_path:
            return jsonify({'error': 'Failed to generate report'}), 500
        
        # Handle JSON report format specially
        if report_format == 'json':
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            
            return jsonify({
                'message': 'Report generated successfully',
                'report_path': report_path,
                'report_data': report_data
            }), 200
        
        return jsonify({
            'message': 'Report generated successfully',
            'report_path': report_path
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_report/<scan_id>', methods=['GET'])
def get_report(scan_id):
    """
    Generate a report for a specific scan
    
    GET parameters:
    - format: Report format (pdf, csv, html, json)
    """
    # Get report format
    report_format = request.args.get('format', 'pdf')
    
    try:
        # Process vulnerabilities
        vulnerabilities = process_vulnerabilities(scan_id)
        
        # Generate report
        report_path = generate_report(
            scan_id=scan_id,
            vulnerabilities=vulnerabilities,
            report_format=report_format
        )
        
        if not report_path:
            return jsonify({'error': 'Failed to generate report'}), 500
        
        # Handle JSON report format specially
        if report_format == 'json':
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            
            return jsonify({
                'message': 'Report generated successfully',
                'report_path': report_path,
                'report_data': report_data
            }), 200
        
        return jsonify({
            'message': 'Report generated successfully',
            'report_path': report_path
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_report/<path:report_path>', methods=['GET'])
def download_report(report_path):
    """
    Download a generated report
    
    Args:
        report_path (str): Path to the report file
    """
    try:
        # Ensure path is within reports directory
        if '../' in report_path:
            return jsonify({'error': 'Invalid report path'}), 400
        
        full_path = os.path.join(os.environ.get('REPORTS_DIR', '../data/reports'), report_path)
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'Report not found'}), 404
        
        # Determine content type based on file extension
        content_type = 'application/octet-stream'
        if full_path.endswith('.pdf'):
            content_type = 'application/pdf'
        elif full_path.endswith('.csv'):
            content_type = 'text/csv'
        elif full_path.endswith('.html'):
            content_type = 'text/html'
        elif full_path.endswith('.json'):
            content_type = 'application/json'
        
        return send_file(
            full_path,
            mimetype=content_type,
            as_attachment=True,
            download_name=os.path.basename(full_path)
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)