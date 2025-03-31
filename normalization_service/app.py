from flask import Flask, request, jsonify
import os
import tempfile
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Import normalization modules
from normalization.normalizer import normalize_source_code
from normalization.clean_gadget import clean_gadget

@app.route('/normalize', methods=['POST'])
def normalize():
    """
    Normalize C/C++ source code
    
    POST parameters:
    - file: C/C++ source file
    - output_path: (Optional) Where to save the normalized file
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
        # Normalize the code
        with open(temp_path, 'r') as f:
            source_code = f.read()
        
        # First pass: clean up comments, string literals, etc.
        normalized_code = normalize_source_code(source_code)
        
        # Second pass: standardize variable and function names
        code_lines = normalized_code.splitlines(True)
        cleaned_lines = clean_gadget(code_lines)
        final_code = ''.join(cleaned_lines)
        
        # Determine output path
        output_path = request.form.get('output_path')
        if not output_path:
            # Default: save to normalized directory
            output_dir = os.environ.get('NORMALIZED_DIR', '../data/normalized')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename)
        
        # Save normalized code
        with open(output_path, 'w') as f:
            f.write(final_code)
        
        return jsonify({
            'message': 'Normalization successful',
            'normalized_path': output_path
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
    app.run(debug=True, host='0.0.0.0', port=5001)