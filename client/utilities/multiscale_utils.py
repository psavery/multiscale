#!/usr/bin/env python

from girder_client import HttpError

from .job_utils import JobUtils

class MultiscaleUtils:


    def __init__(self, gc):
        self.gc = gc


    def getOutputFolder(self, jobId):
        params = { "id" : jobId }
        try:
            resp = self.gc.get(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print("Error. invalid job id:", jobId)
                return {}
            raise

        if not resp:
            return

        metaData = resp.get('meta')

        if not isinstance(metaData, dict):
            return

        if 'multiscale_settings' not in metaData:
            print('Error: this does not appear to be a multiscale job.')
            return

        multiscale_settings = metaData['multiscale_settings']

        if 'outputFolderId' not in multiscale_settings:
            print('Error: outputFolderId is not in multiscale_settings!')
            return

        outputFolderId = multiscale_settings['outputFolderId']
        return self.gc.getFolder(outputFolderId)


    def downloadJobOutput(self, jobId):

        outputFolder = self.getOutputFolder(jobId)

        folderId = outputFolder.get('_id', 'id_unknown')
        folderName = outputFolder.get('name', 'name_unknown')

        self.gc.downloadFolderRecursive(folderId, folderName)

        print('Downloaded output to:', folderName)
