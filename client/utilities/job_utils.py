#!/usr/bin/env python

class JobUtils:

    JOB_LIST_PATH = '/job'
    JOB_ID_PATH = '/job/{id}'
    JOB_CANCEL_PATH = '/job/{id}/cancel'

    JOB_STATUS = {
        0 : 'INACTIVE',
        1 : 'QUEUED',
        2 : 'RUNNING',
        3 : 'SUCCESS',
        4 : 'ERROR',
        5 : 'CANCELED',

        820 : 'FETCHING_INPUT',
        821 : 'CONVERTING_INPUT',
        822 : 'CONVERTING_OUTPUT',
        823 : 'PUSHING_OUTPUT',
        824 : 'CANCELING'
    }


    def __init__(self, gc):
        self.gc = gc


    @staticmethod
    def getJobStatusStr(status):
        if not status:
            return ""

        return JobUtils.JOB_STATUS.get(status, "")


    def jobStatus(self, jobId):
        params = { "id" : jobId }
        resp = self.gc.get(JobUtils.JOB_ID_PATH, parameters=params)

        if not resp:
            return ""

        status = resp.get('status')

        statusStr = JobUtils.getJobStatusStr(status)
        return statusStr


    def cancelJob(self, jobId):
        params = { "id" : jobId }
        resp = self.gc.put(JobUtils.JOB_CANCEL_PATH, parameters=params)

        print('resp is', resp)


    def getAllJobsForUser(self, userId):
        params = { "userId" : userId }
        resp = self.gc.get(JobUtils.JOB_LIST_PATH, parameters=params)

        output = {}
        for job in resp:
            if not job:
                continue
            jobId = job.get('_id')
            status = job.get('status')
            statusStr = JobUtils.getJobStatusStr(status)
            output[jobId] = statusStr

        return output
