from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
from app import db
from models.project import Project
from models.file import File
from models.scan import Scan

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    current_user_id = get_jwt_identity()
    
    projects = Project.query.filter_by(user_id=current_user_id).all()
    
    result = []
    for project in projects:
        project_data = project.to_dict()
        
        # Add additional info
        files_count = File.query.filter_by(project_id=project.id).count()
        scans_count = Scan.query.filter_by(project_id=project.id).count()
        
        # Get latest scan
        latest_scan = Scan.query.filter_by(project_id=project.id).order_by(Scan.started_at.desc()).first()
        
        project_data['files_count'] = files_count
        project_data['scans_count'] = scans_count
        if latest_scan:
            project_data['latest_scan'] = {
                'id': latest_scan.id,
                'status': latest_scan.status,
                'started_at': latest_scan.started_at.isoformat(),
                'vulnerabilities': {
                    'high': latest_scan.high_severity_count,
                    'medium': latest_scan.medium_severity_count,
                    'low': latest_scan.low_severity_count
                }
            }
        
        result.append(project_data)
    
    return jsonify(result), 200

@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    current_user_id = get_jwt_identity()
    
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    project_data = project.to_dict()
    
    # Add additional info
    files = File.query.filter_by(project_id=project.id).all()
    scans = Scan.query.filter_by(project_id=project.id).order_by(Scan.started_at.desc()).all()
    
    project_data['files'] = [file.to_dict() for file in files]
    project_data['scans'] = [scan.to_dict() for scan in scans]
    
    return jsonify(project_data), 200

@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('name'):
        return jsonify({'message': 'Missing project name'}), 400
    
    # Create new project
    project_id = str(uuid.uuid4())
    new_project = Project(
        id=project_id,
        user_id=current_user_id,
        name=data['name'],
        description=data.get('description')
    )
    
    db.session.add(new_project)
    db.session.commit()
    
    return jsonify({
        'message': 'Project created successfully',
        'project': new_project.to_dict()
    }), 201

@projects_bp.route('/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    current_user_id = get_jwt_identity()
    
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    data = request.get_json()
    
    # Update project
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Project updated successfully',
        'project': project.to_dict()
    }), 200

@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    current_user_id = get_jwt_identity()
    
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    # Delete associated records (files, scans, etc.)
    # In a production system, this would likely be handled with a CASCADE delete
    # or a more sophisticated deletion strategy
    files = File.query.filter_by(project_id=project_id).all()
    for file in files:
        db.session.delete(file)
    
    scans = Scan.query.filter_by(project_id=project_id).all()
    for scan in scans:
        db.session.delete(scan)
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': 'Project deleted successfully'}), 200