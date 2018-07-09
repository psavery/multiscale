#!/usr/bin/env python

import os
import sys

import girder_client

from utilities.job_utils import JobUtils

API_URL = 'http://localhost:8080/api/v1'


def getClient(apiKey):
    if not apiKey:
        apiKey = os.getenv('GIRDER_API_KEY')
        if not apiKey:
            sys.exit('An api key is required to run this script. '
                     'See --help for more info')

    gc = girder_client.GirderClient(apiUrl=API_URL)
    gc.authenticate(apiKey=apiKey)

    return gc


def jobStatus(gc, args):
    jobId = args.job_id
    ju = JobUtils(gc)
    statusStr = ju.jobStatus(jobId)
    print('jobId:', jobId)
    print('status:', statusStr)


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
    status.set_defaults(func=jobStatus)

    args = parser.parse_args()

    apiKey = args.api_key
    gc = getClient(apiKey)

    args.func(gc, args)
