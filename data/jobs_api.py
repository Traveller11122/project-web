import flask
from data import db_session
from flask import jsonify
from data.jobs import Jobs
from flask import request


blueprint = flask.Blueprint('jobs_api', __name__,
                            template_folder='templates')


@blueprint.route('/api/jobs')
def get_jobs():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('id', 'job', 'work_size', 'collaborators', 'start_date', 'end_date', 'is_finished',
                                    'team_leader'))
                 for item in jobs]
        }
    )


@blueprint.route('/api/jobs/<int:job_id>',  methods=['GET'])
def get_one_job(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'job': job.to_dict(only=('id', 'job', 'work_size', 'collaborators', 'start_date', 'end_date',
                                     'is_finished', 'team_leader'))
        }
    )


@blueprint.route('/api/news', methods=['POST'])
def create_job():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['team_leader', 'job', 'collaborators', 'work_size']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    jobs = Jobs(
        team_leader=request.json['team_leader'],
        job=request.json['job'],
        work_size=request.json['work_size'],
        collaborators=request.json['collaborators']

    )
    session.add(jobs)
    session.commit()
    return jsonify({'success': 'OK'})


