#!/usr/bin/env python

from girder_client import HttpError

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
        if not isinstance(status, int):
            return ""

        return JobUtils.JOB_STATUS.get(status, "")


    def jobStatus(self, jobId):
        params = { "id" : jobId }
        try:
            resp = self.gc.get(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print("Error. invalid job id:", jobId)
                return {}
            raise

        if not resp:
            return ""

        status = resp.get('status')

        statusStr = JobUtils.getJobStatusStr(status)
        return statusStr


    def getAllJobsForUser(self, userId):
        params = {
            "userId" : userId,
            "limit" : 1000000
        }
        try:
            resp = self.gc.get(JobUtils.JOB_LIST_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print("Error. invalid user id:", userId)
                return {}
            raise

        output = {}
        for job in resp:
            if not job:
                continue
            jobId = job.get('_id')
            status = job.get('status')
            statusStr = JobUtils.getJobStatusStr(status)
            output[jobId] = statusStr

        return output


    def getJobLog(self, jobId):
        params = { "id" : jobId }
        try:
            resp = self.gc.get(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print("Error. invalid job id:", jobId)
                return {}
            raise

        if not resp:
            return ""

        log = resp.get('log', "")
        return log


    def cancelJob(self, jobId):
        params = { "id" : jobId }
        try:
            return self.gc.put(JobUtils.JOB_CANCEL_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print("Error. invalid job id:", jobId)
                return {}
            raise


    def deleteJob(self, jobId):
        params = { "id" : jobId }
        try:
            return self.gc.delete(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print("Error. invalid job id:", jobId)
                return {}
            raise
