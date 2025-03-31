from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import os
from werkzeug.utils import secure_filename
from app import db
from models.file import File
from models.project import Project

files_bp = Blueprint('files', __name__)

@files_bp.route('/projects/<project_id>/files', methods=['GET'])
@jwt_required()
def get_files(project_id):
    current_user_id = get_jwt_identity()
    
    # Validate project
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    files = File.query.filter_by(project_id=project_id).all()
    
    return jsonify([file.to_dict() for file in files]), 200

@files_bp.route('/projects/<project_id>/files/<file_id>', methods=['GET'])
@jwt_required()
def get_file(project_id, file_id):
    current_user_id = get_jwt_identity()
    
    # Validate project
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    file = File.query.filter_by(id=file_id, project_id=project_id).first()
    if not file:
        return jsonify({'message': 'File not found'}), 404
    
    return jsonify(file.to_dict()), 200

@files_bp.route('/projects/<project_id>/files/<file_id>/content', methods=['GET'])
@jwt_required()
def get_file_content(project_id, file_id):
    current_user_id = get_jwt_identity()
    
    # Validate project
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    file = File.query.filter_by(id=file_id, project_id=project_id).first()
    if not file:
        return jsonify({'message': 'File not found'}), 404
    
    # Return file content
    file_path = file.file_path
    if not os.path.exists(file_path):
        return jsonify({'message': 'File not found on disk'}), 404
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({'content': content}), 200
    except Exception as e:
        return jsonify({'message': f'Error reading file: {str(e)}'}), 500

@files_bp.route('/projects/<project_id>/files/<file_id>/download', methods=['GET'])
@jwt_required()
def download_file(project_id, file_id):
    current_user_id = get_jwt_identity()
    
    # Validate project
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    file = File.query.filter_by(id=file_id, project_id=project_id).first()
    if not file:
        return jsonify({'message': 'File not found'}), 404
    
    # Return file for download
    file_path = file.file_path
    if not os.path.exists(file_path):
        return jsonify({'message': 'File not found on disk'}), 404
    
    return send_file(
        file_path,
        mimetype=file.content_type,
        as_attachment=True,
        download_name=file.filename
    )

@files_bp.route('/projects/<project_id>/files', methods=['POST'])
@jwt_required()
def upload_file(project_id):
    current_user_id = get_jwt_identity()
    
    # Validate project
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    # Check if file is provided
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'projects', project_id)
    os.makedirs(upload_dir, exist_ok=True)
    
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
    db.session.commit()
    
    return jsonify({
        'message': 'File uploaded successfully',
        'file': file_record.to_dict()
    }), 201

@files_bp.route('/projects/<project_id>/files/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(project_id, file_id):
    current_user_id = get_jwt_identity()
    
    # Validate project
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    file = File.query.filter_by(id=file_id, project_id=project_id).first()
    if not file:
        return jsonify({'message': 'File not found'}), 404
    
    # Delete file from disk
    file_path = file.file_path
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            # Log error but continue
            print(f"Error deleting file from disk: {str(e)}")
    
    # Delete from database
    db.session.delete(file)
    db.session.commit()
    
    return jsonify({'message': 'File deleted successfully'}), 200