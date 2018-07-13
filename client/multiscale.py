#!/usr/bin/env python3

"""
Multiscale client.

This is a client tool to submit, check status, and clean up
multiscale modeling jobs that are to run on a girder server.

See --help for options.
"""

import os
import sys

import girder_client
from girder_client import HttpError

from calculations.albany import submitAlbanyCalculation
from calculations.dream3d import submitDream3DJob
from calculations.smtk_mesh_placement import submitSmtkMeshPlacement

from utilities.folder_utils import FolderUtils
from utilities.progress_bar import progress_bar
from utilities.job_utils import JobUtils
from utilities.multiscale_utils import MultiscaleUtils
from utilities.user_utils import UserUtils
from utilities.query_yes_no import query_yes_no

DEFAULT_API_URL = 'http://localhost:8080/api/v1'

supportedCalculations = [
    'albany',
    'dream3d',
    'smtk'
]


def getClient(apiUrl, apiKey):
    """Get an authenticated GirderClient object.

    Takes an apiUrl and an apiKey and returns an authenticated
    girder_client.GirderClient object.

    If the apiUrl is empty or set to "None", the environment variable
    "MULTISCALE_API_URL" will be used. If it is not set, the
    default http://localhost:8080/api/v1 value will be used instead.

    If the apiKey is empty or set to "None", the environment variable
    "MULTISCALE_API_KEY" will be used. A valid api key is mandatory.
    """
    if not apiUrl:
        apiUrl = os.getenv('MULTISCALE_API_URL')
        if not apiUrl:
            apiUrl = DEFAULT_API_URL

    if not apiKey:
        apiKey = os.getenv('MULTISCALE_API_KEY')
        if not apiKey:
            sys.exit('An api key is required to run this script. '
                     'See --help for more info')

    progress_bar.reportProgress = sys.stdout.isatty()

    gc = girder_client.GirderClient(apiUrl=apiUrl,
                                    progressReporterCls=progress_bar)

    try:
        gc.authenticate(apiKey=apiKey)
    except HttpError as e:
        if e.status == 500:
            print('Error: invalid api key')
            return None

        raise

    return gc


def submitFunc(gc, args):
    """Submit a multiscale calculation."""
    calcType = args.calculation_type.lower()
    inputDir = args.input_dir

    if calcType == 'albany':
        submitAlbanyCalculation(gc, inputDir)
    elif calcType == 'smtk':
        submitSmtkMeshPlacement(gc, inputDir)
    elif calcType == 'dream3d':
        submitDream3DJob(gc, inputDir)
    else:
        print('Error: unsupported calculation type:', calcType)


def statusFunc(gc, args):
    """Get the status of a multiscale job."""
    jobId = args.job_id
    ju = JobUtils(gc)
    statusStr = ju.jobStatus(jobId)

    if not statusStr:
        return

    print('jobId:', jobId)
    print('status:', statusStr)


def listFunc(gc, args):
    """List all jobs for the current user."""
    uu = UserUtils(gc)
    userId = uu.getCurrentUserId()

    ju = JobUtils(gc)
    jobList = ju.getAllJobsForUser(userId)

    if not jobList:
        print('No jobs found')
        return

    print('=' * 59)
    print('{:30s} {:12s} {:15s}'.format('jobId', 'status', 'run time (wall)'))
    print('=' * 59)
    for jobId in jobList.keys():
        print('{:30s} {:12s} {:15s}'.format(jobId, jobList[jobId],
                                            ju.getWallTime(jobId)))


def logFunc(gc, args):
    """Display the job log for a given job id."""
    jobId = args.job_id
    ju = JobUtils(gc)
    log = ju.getJobLog(jobId)
    for entry in log:
        print(entry)


def downloadFunc(gc, args):
    """Download the input or output of a specified job."""
    jobId = args.job_id
    download_input = args.download_input

    mu = MultiscaleUtils(gc)

    if download_input:
        mu.downloadJobInput(jobId)
    else:
        ju = JobUtils(gc)
        statusStr = ju.jobStatus(jobId)
        if statusStr != 'SUCCESS':
            print('Warning: job status is not "SUCCESS". The output may '
                  'be missing or invalid')
        mu.downloadJobOutput(jobId)


def cancelFunc(gc, args):
    """Cancel a running or inactive job."""
    jobId = args.job_id
    ju = JobUtils(gc)
    ju.cancelJob(jobId)


def deleteFunc(gc, args):
    """Delete a job and all of its input and output."""
    jobId = args.job_id
    ju = JobUtils(gc)

    # If it is a multiscale job, we may want to delete the output directory
    deleteFolderId = None
    mu = MultiscaleUtils(gc)
    fu = FolderUtils(gc)
    if mu.isMultiscaleJob(jobId):
        folderId = mu.getJobFolderId(jobId)
        folderPath = fu.getFullFolderPath(folderId)
        question = ('This will permanently delete the output folder for this '
                    'job and all of its contents.\nThe output folder is: ' +
                    folderPath + '\nAre you sure you want to delete this?')
        if not query_yes_no(question, default='no'):
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
    """Delete all jobs that are not inactive, queued, or running.

    This will also delete all input and output for each job that
    is deleted.
    """
    uu = UserUtils(gc)
    userId = uu.getCurrentUserId()

    # Double check with the user since this can be significant and irreversible
    question = ('This will permanently delete all jobs and outputs for '
                'userId: \n"' + str(userId) + '"\nexcept for jobs that are '
                'currently inactive, queued, or running\n'
                'Are you completely sure that you want to do this?')
    if not query_yes_no(question, default='no'):
        return

    ju = JobUtils(gc)
    jobList = ju.getAllJobsForUser(userId)

    if not jobList:
        return

    mu = MultiscaleUtils(gc)
    fu = FolderUtils(gc)
    for jobId in jobList.keys():
        if jobList[jobId] == 'INACTIVE':
            continue
        elif jobList[jobId] == 'QUEUED':
            continue
        elif jobList[jobId] == 'RUNNING':
            continue
        else:
            folderId = None
            if mu.isMultiscaleJob(jobId):
                folderId = mu.getJobFolderId(jobId)

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

    parser.add_argument('-u', '--api-url',
                        help='The api url for the girder server. '
                             'The default is the local host. '
                             'Note: the url normally ends in /api/v1')

    sub = parser.add_subparsers()
    submit = sub.add_parser('submit', help=('Submit a multiscale job along '
                                            'with its input folder.'))
    submit.add_argument(
        'calculation_type',
        help=(
            'The type of simulation to '
            'perform. Current supported '
            'types are: ' +
            ', '.join(supportedCalculations)))
    submit.add_argument(
        'input_dir', help=(
            'The directory containing all input '
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
    download.add_argument('-i', '--download-input', action='store_true',
                          help=('Instead of downloading the output for this '
                                'job, download the input.'))
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
    apiUrl = args.api_url
    gc = getClient(apiUrl, apiKey)

    if not gc:
        sys.exit()

    args.func(gc, args)
