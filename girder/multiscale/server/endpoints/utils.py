"""Utilities for the multiscale endpoint functions."""

from girder.plugins.jobs.models.job import Job


def setMultiscaleMetaData(jobId, inputFolderId, outputFolderId):
    """Set the multiscale meta data for the jobId.

    Currently, we use this to keep track of the input and output
    folders.

    Returns the updated job.
    """
    # We want to update the job with some multiscale settings.
    # We will put it in the meta data.
    job = Job().findOne({'_id': jobId})
    multiscale_io = {
        'meta': {
            'multiscale_settings': {
                'inputFolderId': inputFolderId,
                'outputFolderId': outputFolderId
            }
        }
    }

    return Job().updateJob(job, otherFields=multiscale_io)
