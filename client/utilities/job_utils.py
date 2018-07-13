"""Job utility functions for communicating with girder."""

from girder_client import HttpError

from datetime import datetime, timezone


class JobUtils:
    """Utility functions for performing job operations on girder."""

    JOB_LIST_PATH = '/job'
    JOB_ID_PATH = '/job/{id}'
    JOB_CANCEL_PATH = '/job/{id}/cancel'

    JOB_STATUS = {
        0: 'INACTIVE',
        1: 'QUEUED',
        2: 'RUNNING',
        3: 'SUCCESS',
        4: 'ERROR',
        5: 'CANCELED',

        820: 'FETCHING_INPUT',
        821: 'CONVERTING_INPUT',
        822: 'CONVERTING_OUTPUT',
        823: 'PUSHING_OUTPUT',
        824: 'CANCELING'
    }

    def __init__(self, gc):
        """Initialize with an authenticated GirderClient object."""
        self.gc = gc

    @staticmethod
    def getJobStatusStr(status):
        """Get a job status string from a status id number."""
        if not isinstance(status, int):
            return ''

        return JobUtils.JOB_STATUS.get(status, '')

    def jobStatus(self, jobId):
        """Get a job status string from a job id number."""
        params = {'id': jobId}
        try:
            resp = self.gc.get(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print('Error. invalid job id:', jobId)
                return {}
            raise

        if not resp:
            return ''

        status = resp.get('status')

        statusStr = JobUtils.getJobStatusStr(status)
        return statusStr

    def getAllJobsForUser(self, userId):
        """Get all jobs for a specified user id.

        Returns a dictionary of jobIds to status strings.
        """
        params = {
            'userId': userId,
            'limit': 1000000
        }
        try:
            resp = self.gc.get(JobUtils.JOB_LIST_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print('Error. invalid user id:', userId)
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
        """Get the log for a given jobId."""
        params = {'id': jobId}
        try:
            resp = self.gc.get(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print('Error. invalid job id:', jobId)
                return {}
            raise

        if not resp:
            return ''

        log = resp.get('log', '')
        return log

    def cancelJob(self, jobId):
        """Cancel a job given its jobId."""
        params = {'id': jobId}
        try:
            return self.gc.put(JobUtils.JOB_CANCEL_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print('Error. invalid job id:', jobId)
                return {}
            raise

    def deleteJob(self, jobId):
        """Delete a job given its jobId."""
        params = {'id': jobId}
        try:
            return self.gc.delete(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print('Error. invalid job id:', jobId)
                return {}
            raise

    @staticmethod
    def isoStrToDatetime(isoStr):
        """Convert iso string to datetime.

        Unfortunately, python does not currently have an easy way to
        do this. A datetime.fromisoformat was added in python 3.7, but
        we do not require that version of python yet.

        See this issue:
        https://stackoverflow.com/questions/28331512/how-to-convert-python-isoformat-string-back-into-datetime-object
        """
        split = isoStr.rsplit(':', 1)
        modifiedStr = split[0] + split[1]
        return datetime.strptime(modifiedStr, '%Y-%m-%dT%H:%M:%S.%f%z')

    def getWallTime(self, jobId):
        """Get the total elapsed wall time (seconds) since the job started."""
        params = {'id': jobId}
        try:
            resp = self.gc.get(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print('Error. invalid job id:', jobId)
                return {}
            raise

        if not resp:
            return ''

        timestamps = resp.get('timestamps', None)
        if not timestamps:
            return ''

        startTime = None
        endTime = None

        for stamp in timestamps:
            status = stamp.get('status', -1)
            if not startTime and JobUtils.getJobStatusStr(status) == 'RUNNING':
                startTime = JobUtils.isoStrToDatetime(stamp.get('time', ''))
                continue
            if startTime and JobUtils.getJobStatusStr(status) != 'RUNNING':
                endTime = JobUtils.isoStrToDatetime(stamp.get('time', ''))
                break

        if not startTime:
            return ''

        if not endTime:
            endTime = datetime.now(timezone.utc)

        return str(endTime - startTime)
