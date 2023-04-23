import flask
from flask import jsonify
from . import db_session
from .jobs import Jobs

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/jobs')
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('team_leader',
                                    'job',
                                    'work_size',
                                    'collaborators',
                                    'start_date',
                                    'is_finished'))
                 for item in jobs]
        }
    )


@blueprint.route('/api/jobs/<int:jobs_id>', methods=['GET'])
def get_one_jobs(jobs_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).get(jobs_id)
    if not jobs:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'jobs': jobs.to_dict(only=('team_leader',
                                       'job',
                                       'work_size',
                                       'collaborators',
                                       'start_date',
                                       'is_finished'))
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def create_jobs():
    if not flask.request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in flask.request.json for key in
                 ['team_leader',
                  'job',
                  'work_size',
                  'collaborators',
                  'is_finished']):
        return jsonify({'error': 'Bad request'})
    elif type(flask.request.json['work_size']) != int:
        return jsonify({'error': 'Bad request'})
    elif type(flask.request.json['team_leader']) != int:
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    jobs = Jobs(
        team_leader=flask.request.json['team_leader'],
        job=flask.request.json['job'],
        work_size=flask.request.json['work_size'],
        collaborators=flask.request.json['collaborators'],
        is_finished=flask.request.json['is_finished']
    )
    db_sess.add(jobs)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:jobs_id>', methods=['DELETE'])
def delete_jobs(jobs_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).get(jobs_id)
    if not jobs:
        return jsonify({'error': 'Not found'})
    db_sess.delete(jobs)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:jobs_id>', methods=['PUT'])
def put_jobs(jobs_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == jobs_id).first()
    if not jobs:
        return jsonify({'error': 'Not found'})
    elif not all(key in flask.request.json for key in
                 ['team_leader',
                  'job',
                  'work_size',
                  'collaborators',
                  'is_finished']):
        return jsonify({'error': 'Bad request'})
    jobs.team_leader = flask.request.json['team_leader']
    jobs.job = flask.request.json['job']
    jobs.work_size = flask.request.json['work_size']
    jobs.collaborators = flask.request.json['collaborators']
    jobs.is_finished = flask.request.json['is_finished']
    db_sess.commit()
    return jsonify(
        {
            'jobs': jobs.to_dict(only=('team_leader',
                                       'job',
                                       'work_size',
                                       'collaborators',
                                       'start_date',
                                       'is_finished'))
        }
    )
