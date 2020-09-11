from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from collections import OrderedDict
from flask import current_app, request, Response
from .json import jsonify

"""Gets the scheduler info."""
def get_scheduler_info():
    scheduler = current_app.apscheduler

    d = OrderedDict([
        ('current_host', scheduler.host_name),
        ('allowed_hosts', scheduler.allowed_hosts),
        ('running', scheduler.running)
    ])

    return jsonify(d)

"""Adds a new job."""
def add_job():
    data = request.get_json(force=True)

    try:
        job = current_app.apscheduler.add_job(**data)
        return jsonify(job)
    except ConflictingIdError:
        return jsonify(dict(error_message='Job %s already exists.' % data.get('id')), status=409)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)

"""Deletes a job."""
def delete_job(job_id):
    try:
        current_app.apscheduler.remove_job(job_id)
        return Response(status=204)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)

"""Gets a job."""
def get_job(job_id):
    job = current_app.apscheduler.get_job(job_id)

    if not job:
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)

    return jsonify(job)

"""Gets all scheduled jobs."""
def get_jobs():
    jobs = current_app.apscheduler.get_jobs()

    job_states = []

    for job in jobs:
        job_states.append(job)

    return jsonify(job_states)

"""Updates a job."""
def update_job(job_id):
    data = request.get_json(force=True)

    try:
        current_app.apscheduler.modify_job(job_id, **data)
        job = current_app.apscheduler.get_job(job_id)
        return jsonify(job)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)

"""Pauses a job."""
def pause_job(job_id):
    try:
        current_app.apscheduler.pause_job(job_id)
        job = current_app.apscheduler.get_job(job_id)
        return jsonify(job)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)

"""Resumes a job."""
def resume_job(job_id):
    try:
        current_app.apscheduler.resume_job(job_id)
        job = current_app.apscheduler.get_job(job_id)
        return jsonify(job)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)

"""Executes a job."""
def run_job(job_id):
    try:
        current_app.apscheduler.run_job(job_id)
        job = current_app.apscheduler.get_job(job_id)
        return jsonify(job)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)