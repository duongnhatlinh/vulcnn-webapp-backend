from flask import Flask, request, jsonify
import os
import tempfile
import pickle
import networkx as nx
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Import image generator modules
from generator.image_generator import generate_image_representation
from generator.sent2vec_wrapper import load_sent2vec_model

# Load Sent2Vec model at startup
sent2vec_model = None
@app.before_first_request
def initialize():
    global sent2vec_model
    model_path = os.environ.get('SENT2VEC_MODEL_PATH', '../models/sent2vec_model.bin')
    sent2vec_model = load_sent2vec_model(model_path)

@app.route('/generate_image', methods=['POST'])
def generate_image():
    """
    Generate an image representation from a PDG file
    
    POST parameters:
    - pdg_file: PDG file in DOT format
    - output_path: (Optional) Where to save the generated image
    """
    global sent2vec_model
    
    # Check if model is loaded
    if sent2vec_model is None:
        return jsonify({'error': 'Sent2Vec model not initialized'}), 500
    
    # Check if file was uploaded
    if 'pdg_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['pdg_file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check file extension
    if not file.filename.endswith('.dot'):
        return jsonify({'error': 'File must be in DOT format'}), 400
    
    # Save the uploaded file to a temporary location
    filename = secure_filename(file.filename)
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, filename)
    file.save(temp_path)
    
    try:
        # Load the PDG from the DOT file
        pdg = nx.drawing.nx_pydot.read_dot(temp_path)
        
        # Determine output path
        output_path = request.form.get('output_path')
        if not output_path:
            # Default: save to images directory
            output_dir = os.environ.get('IMAGES_DIR', '../data/images')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.pkl")
        
        # Generate image representation
        image_data = generate_image_representation(pdg, sent2vec_model)
        
        # Save image representation
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            pickle.dump(image_data, f)
        
        return jsonify({
            'message': 'Image generation successful',
            'image_path': output_path
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
    status = 'ok' if sent2vec_model is not None else 'model not loaded'
    return jsonify({'status': status}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)