#!/usr/bin/env python

import os
import sys

import girder_client
from girder_client import HttpError

from utilities.job_utils import JobUtils
from utilities.user_utils import UserUtils
from utilities.query_yes_no import query_yes_no

API_URL = 'http://localhost:8080/api/v1'

def getClient(apiKey):
    if not apiKey:
        apiKey = os.getenv('GIRDER_API_KEY')
        if not apiKey:
            sys.exit('An api key is required to run this script. '
                     'See --help for more info')

    gc = girder_client.GirderClient(apiUrl=API_URL)

    try:
        gc.authenticate(apiKey=apiKey)
    except HttpError as e:
        if e.status == 500:
            print("Error: invalid api key")
            return None

        raise

    return gc


def statusFunc(gc, args):
    jobId = args.job_id
    ju = JobUtils(gc)
    statusStr = ju.jobStatus(jobId)

    if not statusStr:
        return

    print('jobId:', jobId)
    print('status:', statusStr)


def listFunc(gc, args):
    uu = UserUtils(gc)
    userId = uu.getCurrentUserId()

    ju = JobUtils(gc)
    jobList = ju.getAllJobsForUser(userId)

    if not jobList:
        print("No jobs found")
        return

    print('=' * 40)
    print('{:30s} {:8s}'.format('jobId', 'status'))
    print('=' * 40)
    for jobId in jobList.keys():
        print('{:30s} {:8s}'.format(jobId, jobList[jobId]))


def cancelFunc(gc, args):
    jobId = args.job_id
    ju = JobUtils(gc)
    ju.cancelJob(jobId)


def deleteFunc(gc, args):
    jobId = args.job_id
    ju = JobUtils(gc)

    # Make sure the job isn't running first. If it is, cancel it first.
    statusStr = ju.jobStatus(jobId)
    if statusStr == 'RUNNING':
        print('Job is currently running. Canceling first...')
        ju.cancelJob(jobId)
    if statusStr == 'RUNNING' or statusStr == 'CANCELING':
        print('Job is canceling. Please wait...')
        while ju.jobStatus(jobId) != 'CANCELED':
            continue

    ju.deleteJob(jobId)


def cleanFunc(gc, args):
    uu = UserUtils(gc)
    userId = uu.getCurrentUserId()

    # Double check with the user since this can be significant and irreversible
    question = ('This will permanently delete all jobs and outputs for '
                'userId: \n"' + str(userId) + '"\nexcept for jobs that are '
                'currently inactive, queued, or running\n'
                'Are you completely sure that you want to do this?')
    if not query_yes_no(question, default="no"):
        return

    ju = JobUtils(gc)
    jobList = ju.getAllJobsForUser(userId)

    if not jobList:
        return

    for jobId in jobList.keys():
        if jobList[jobId] == "INACTIVE":
            continue
        elif jobList[jobId] == "QUEUED":
            continue
        elif jobList[jobId] == "RUNNING":
            continue
        else:
            ju.deleteJob(jobId)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-k', '--api-key',
                        help='A valid api key for accessing girder. '
                             'Alternatively, the environment variable '
                             '"GIRDER_API_KEY" may be set instead.')

    sub = parser.add_subparsers()
    status = sub.add_parser('status', help='Get the job status for a '
                                           'given job id.')
    status.add_argument('job_id', help='The job id')
    status.set_defaults(func=statusFunc)

    listJobs = sub.add_parser('list', help='Get the list of jobs and their'
                                           'statuses for the current user.')
    listJobs.set_defaults(func=listFunc)

    cancel = sub.add_parser('cancel', help='Cancel a job for a given job id.')
    cancel.add_argument('job_id', help='The job id')
    cancel.set_defaults(func=cancelFunc)

    delete = sub.add_parser('delete', help='Delete a job with a given job id.')
    delete.add_argument('job_id', help='The job id')
    delete.set_defaults(func=deleteFunc)

    clean = sub.add_parser('clean', help='Delete all jobs that are not '
                                         'inactive, queued, or running '
                                         'for the current user.')
    clean.set_defaults(func=cleanFunc)

    args = parser.parse_args()

    if not getattr(args, 'func', None):
        parser.print_help()
        sys.exit()

    apiKey = args.api_key
    gc = getClient(apiKey)

    if not gc:
        sys.exit()

    args.func(gc, args)
