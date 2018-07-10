#!/usr/bin/env python3

import os
import sys

import girder_client
from girder_client import HttpError

from calculations.albany import submitAlbanyCalculation

from utilities.folder_utils import FolderUtils
from utilities.job_utils import JobUtils
from utilities.multiscale_utils import MultiscaleUtils
from utilities.user_utils import UserUtils
from utilities.query_yes_no import query_yes_no

API_URL = 'http://localhost:8080/api/v1'

def getClient(apiKey):
    if not apiKey:
        apiKey = os.getenv('MULTISCALE_API_KEY')
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


def submitFunc(gc, args):
    calcType = args.calculation_type.lower()
    inputDir = args.input_dir

    if calcType == 'albany':
        submitAlbanyCalculation(gc, inputDir)
    else:
        print("Error: unsupported calculation type:", calcType)


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


def logFunc(gc, args):
    jobId = args.job_id
    ju = JobUtils(gc)
    log = ju.getJobLog(jobId)
    for entry in log:
        print(entry)


def downloadFunc(gc, args):
    jobId = args.job_id

    ju = JobUtils(gc)
    statusStr = ju.jobStatus(jobId)
    if statusStr != 'SUCCESS':
        print('Warning: job status is not "SUCCESS". The output may '
              'be missing or invalid')

    mu = MultiscaleUtils(gc)
    mu.downloadJobOutput(jobId)


def cancelFunc(gc, args):
    jobId = args.job_id
    ju = JobUtils(gc)
    ju.cancelJob(jobId)


def deleteFunc(gc, args):
    jobId = args.job_id
    ju = JobUtils(gc)

    # If it is a multiscale job, we may want to delete the output directory
    deleteFolderId = None
    mu = MultiscaleUtils(gc)
    fu = FolderUtils(gc)
    if mu.isMultiscaleJob(jobId):
        folderId = mu.getOutputFolderId(jobId)
        folderPath = fu.getFullFolderPath(folderId)
        question = ('This will permanently delete the output folder for this '
                    'job and all of its contents.\nThe output folder is: ' +
                    folderPath + '\nAre you sure you want to delete this?')
        if not query_yes_no(question, default="no"):
            return

        deleteFolderId = folderId

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

    if deleteFolderId:
        fu.deleteFolder(deleteFolderId)


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

    mu = MultiscaleUtils(gc)
    fu = FolderUtils(gc)
    for jobId in jobList.keys():
        if jobList[jobId] == "INACTIVE":
            continue
        elif jobList[jobId] == "QUEUED":
            continue
        elif jobList[jobId] == "RUNNING":
            continue
        else:
            folderId = None
            if mu.isMultiscaleJob(jobId):
                folderId = mu.getOutputFolderId(jobId)

            ju.deleteJob(jobId)

            if folderId:
                fu.deleteFolder(folderId)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-k', '--api-key',
                        help='A valid api key for accessing girder. '
                             'Alternatively, the environment variable '
                             '"MULTISCALE_API_KEY" may be set instead.')

    sub = parser.add_subparsers()
    submit = sub.add_parser('submit', help='Submit a folder')
    submit.add_argument('calculation_type', help=('The type of simulation to '
                                                  'perform. Current supported '
                                                  'types are: albany'))
    submit.add_argument('input_dir', help=('The directory containing all input '
                                           'files that will be uploaded to '
                                           'Girder and used for the '
                                           'simulation'))
    submit.set_defaults(func=submitFunc)

    status = sub.add_parser('status', help='Get the job status for a '
                                           'given job id.')
    status.add_argument('job_id', help='The job id')
    status.set_defaults(func=statusFunc)

    listJobs = sub.add_parser('list', help='Get the list of jobs and their '
                                           'statuses for the current user.')
    listJobs.set_defaults(func=listFunc)

    log = sub.add_parser('log', help='Print the log for a given job id.')
    log.add_argument('job_id', help='The job id')
    log.set_defaults(func=logFunc)

    download = sub.add_parser('download', help=('Download the output folder '
                                                'for a given multiscale '
                                                'job id.'))
    download.add_argument('job_id', help='The job id')
    download.set_defaults(func=downloadFunc)

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
