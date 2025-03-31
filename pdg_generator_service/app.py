from flask import Flask, request, jsonify
import os
import tempfile
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Import PDG generator modules
from generator.pdg_generator import generate_pdg_from_file
from generator.joern_wrapper import run_joern_analysis

@app.route('/generate_pdg', methods=['POST'])
def generate_pdg():
    """
    Generate a Program Dependency Graph (PDG) from a C/C++ source file
    
    POST parameters:
    - file: Normalized C/C++ source file
    - output_path: (Optional) Where to save the generated PDG
    """
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check file extension
    allowed_extensions = {'.c', '.cpp', '.h', '.hpp'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({'error': 'File type not supported'}), 400
    
    # Save the uploaded file to a temporary location
    filename = secure_filename(file.filename)
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, filename)
    file.save(temp_path)
    
    try:
        # Determine output path
        output_path = request.form.get('output_path')
        if not output_path:
            # Default: save to pdgs directory
            output_dir = os.environ.get('PDGS_DIR', '../data/pdgs')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{filename}.dot")
        
        # Generate PDG
        joern_result = run_joern_analysis(temp_path)
        if not joern_result:
            return jsonify({'error': 'Joern analysis failed'}), 500
        
        # Convert Joern output to PDG
        pdg_result = generate_pdg_from_file(joern_result, output_path)
        if not pdg_result:
            return jsonify({'error': 'PDG generation failed'}), 500
        
        return jsonify({
            'message': 'PDG generation successful',
            'pdg_path': output_path
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)