from flask import jsonify, request
from .models import Project, Measure
from . import db, app
from datetime import datetime

@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    
    projects_data = []
    for project in projects:
        measures = Measure.query.filter_by(project_id=project.id).all()
        project_data = {
            'id': project.id,
            'title': project.title,
            'status': project.status,
            'measures': [{'id': measure.id, 'measure_type': measure.measure_type, 'install_date': measure.install_date} for measure in measures]
        }
        projects_data.append(project_data)
    
    return jsonify(projects_data)

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    
    try:
        # Create new project
        project = Project(
            title=data['title'],
            status=data['status']
        )
        db.session.add(project)
        db.session.flush()  # To obtain the project ID

        # Add measures if any
        if 'measures' in data:
            for measure_data in data['measures']:
                measure = Measure(
                    project_id=project.id,
                    measure_type=measure_data['measure_type'],
                    install_date=datetime.strptime(measure_data['install_date'], '%Y-%m-%d').date()
                )
                db.session.add(measure)

        db.session.commit()
        return jsonify({'message': 'Project created successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/measures', methods=['POST'])
def create_measure():
    data = request.json
    
    try:
        measure = Measure(
            project_id=data['project_id'],
            measure_type=data['measure_type'],
            install_date=datetime.strptime(data['install_date'], '%Y-%m-%d').date()
        )
        db.session.add(measure)
        db.session.commit()
        return jsonify({'message': 'Measure created successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/projects/search', methods=['GET'])
def search_projects():
    search_term = request.args.get('q', '')
    
    projects = Project.query.filter(
        Project.title.ilike(f'%{search_term}%')
    ).all()
    
    return jsonify([{
        'id': project.id,
        'title': project.title
    } for project in projects])
