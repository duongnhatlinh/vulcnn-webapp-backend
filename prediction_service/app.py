from flask import Flask, request, jsonify
import os
import tempfile
import pickle
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Import prediction modules
from predictor.vulcnn import VulCNN
from models.model import load_model

# Load VulCNN model at startup
vulcnn_model = None
@app.before_first_request
def initialize():
    global vulcnn_model
    model_path = os.environ.get('VULCNN_MODEL_PATH', '../models/vulcnn_model.h5')
    vulcnn_model = load_model(model_path)

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict vulnerabilities from an image representation
    
    POST parameters:
    - image_file: Image representation file (.pkl)
    - file_id: (Optional) ID of the original source file
    """
    global vulcnn_model
    
    # Check if model is loaded
    if vulcnn_model is None:
        return jsonify({'error': 'VulCNN model not initialized'}), 500
    
    # Check if file was uploaded
    if 'image_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image_file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check file extension
    if not file.filename.endswith('.pkl'):
        return jsonify({'error': 'File must be a pickle file'}), 400
    
    # Save the uploaded file to a temporary location
    filename = secure_filename(file.filename)
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, filename)
    file.save(temp_path)
    
    try:
        # Load the image representation from the pickle file
        with open(temp_path, 'rb') as f:
            image_data = pickle.load(f)
        
        # Get file_id from request if available
        file_id = request.form.get('file_id')
        
        # Run prediction
        predictor = VulCNN(vulcnn_model)
        result = predictor.predict(image_data)
        
        # Process prediction result
        vulnerabilities = []
        if result['is_vulnerable']:
            # Get vulnerability details
            vuln_type = result.get('vulnerability_type', 'Unknown')
            
            # Map to standard vulnerability types based on prediction
            vuln_info = map_vulnerability_type(vuln_type)
            
            # Add additional information
            vulnerability = {
                'file_id': file_id,
                'function_name': result.get('function_name', 'Unknown'),
                'line_number': result.get('line_number', 0),
                'severity': vuln_info.get('severity', 'medium'),
                'type': vuln_info.get('type', 'Unknown'),
                'cwe_id': vuln_info.get('cwe_id', 'CWE-0'),
                'description': vuln_info.get('description', 'Potential vulnerability detected'),
                'confidence_score': result.get('confidence', 0.5)
            }
            vulnerabilities.append(vulnerability)
        
        return jsonify({
            'is_vulnerable': result['is_vulnerable'],
            'vulnerabilities': vulnerabilities
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

def map_vulnerability_type(vuln_type):
    """Map predicted vulnerability type to standard information"""
    # This is a simple mapping - in a real system, this would be more sophisticated
    vulnerability_mapping = {
        'buffer_overflow': {
            'type': 'Buffer Overflow',
            'severity': 'high',
            'cwe_id': 'CWE-119',
            'description': 'A buffer overflow condition exists when a program attempts to put more data in a buffer than it can hold.'
        },
        'format_string': {
            'type': 'Format String Vulnerability',
            'severity': 'high',
            'cwe_id': 'CWE-134',
            'description': 'Uncontrolled format string can lead to data leakage or code execution.'
        },
        'integer_overflow': {
            'type': 'Integer Overflow',
            'severity': 'medium',
            'cwe_id': 'CWE-190',
            'description': 'An integer overflow condition exists when an integer is incremented to a value too large to be stored in the allocated space.'
        },
        'resource_leak': {
            'type': 'Resource Leak',
            'severity': 'low',
            'cwe_id': 'CWE-772',
            'description': 'The program does not release a resource after it has been used.'
        },
        # Add more mappings as needed
    }
    
    return vulnerability_mapping.get(vuln_type, {
        'type': 'Unknown',
        'severity': 'medium',
        'cwe_id': 'CWE-0',
        'description': 'Potential vulnerability detected'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    status = 'ok' if vulcnn_model is not None else 'model not loaded'
    return jsonify({'status': status}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)