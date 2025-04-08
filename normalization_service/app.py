from flask import Flask, request, jsonify
import os
import tempfile
import re
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
        # Step 1: First pass normalization - read and normalize the code
        with open(temp_path, 'r') as f:
            source_code = f.read()
        
        # Remove comments and normalize whitespace
        normalized_code = normalize_source_code(source_code)
        
        # Write normalized code back to temp file
        with open(temp_path, 'w') as f:
            f.write(normalized_code)
        
        # Step 2: Second pass normalization - clean gadget (standardize variable and function names)
        with open(temp_path, 'r') as f:
            code_lines = f.readlines()
        
        cleaned_lines = clean_gadget(code_lines)
        
        # Determine output path
        output_path = request.form.get('output_path')
        if not output_path:
            # Default: save to normalized directory
            output_dir = os.environ.get('NORMALIZED_DIR', '../data/normalized')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save normalized code to output location
        with open(output_path, 'w') as f:
            f.writelines(cleaned_lines)
        
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

@app.route('/normalize_cmd', methods=['POST'])
def normalize_cmd():
    """
    Normalize C/C++ source code provided directly in the request
    
    POST parameters:
    - code: C/C++ source code as text
    """
    data = request.get_json()
    
    if not data or 'code' not in data:
        return jsonify({'error': 'No code provided'}), 400
    
    source_code = data['code']
    
    try:
        # First pass: normalize code
        normalized_code = normalize_source_code(source_code)
        
        # Second pass: clean gadget
        code_lines = normalized_code.splitlines(True)
        cleaned_lines = clean_gadget(code_lines)
        
        final_code = ''.join(cleaned_lines)
        
        return jsonify({
            'message': 'Normalization successful',
            'normalized_code': final_code
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch_normalize', methods=['POST'])
def batch_normalize():
    """
    Normalize multiple files in a directory structure
    
    POST parameters (JSON):
    - input_dir: Directory with source files to normalize
    - output_dir: Directory to save normalized files
    - recursive: Whether to process subdirectories (default: false)
    """
    data = request.get_json()
    
    if not data or 'input_dir' not in data or 'output_dir' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    input_dir = data['input_dir']
    output_dir = data['output_dir']
    recursive = data.get('recursive', False)
    
    if not os.path.isdir(input_dir):
        return jsonify({'error': 'Input directory does not exist'}), 400
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Process files
        processed_files = []
        failed_files = []
        
        def process_directory(dir_path, out_dir, relative_path=''):
            nonlocal processed_files, failed_files
            
            # Create corresponding output directory
            current_out_dir = os.path.join(out_dir, relative_path)
            os.makedirs(current_out_dir, exist_ok=True)
            
            # Process files in current directory
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                
                if os.path.isfile(item_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    if file_ext in ('.c', '.cpp', '.h', '.hpp'):
                        try:
                            # Read source code
                            with open(item_path, 'r') as f:
                                source_code = f.read()
                            
                            # First pass normalization
                            normalized_code = normalize_source_code(source_code)
                            
                            # Second pass normalization
                            code_lines = normalized_code.splitlines(True)
                            cleaned_lines = clean_gadget(code_lines)
                            
                            # Save normalized code
                            output_path = os.path.join(current_out_dir, item)
                            with open(output_path, 'w') as f:
                                f.writelines(cleaned_lines)
                            
                            processed_files.append(os.path.join(relative_path, item))
                        
                        except Exception as e:
                            failed_files.append({
                                'file': os.path.join(relative_path, item),
                                'error': str(e)
                            })
                
                elif os.path.isdir(item_path) and recursive:
                    # Process subdirectory recursively
                    new_relative_path = os.path.join(relative_path, item)
                    process_directory(item_path, out_dir, new_relative_path)
        
        # Start processing from input directory
        process_directory(input_dir, output_dir)
        
        return jsonify({
            'message': 'Batch normalization completed',
            'processed_files': processed_files,
            'failed_files': failed_files,
            'stats': {
                'total': len(processed_files) + len(failed_files),
                'success': len(processed_files),
                'failed': len(failed_files)
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)