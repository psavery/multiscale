#!/usr/bin/env python3

from girder_client import HttpError

from .job_utils import JobUtils

class MultiscaleUtils:


    RUN_ALBANY_PATH = '/multiscale/run_albany_from_girder_folder'


    def __init__(self, gc):
        self.gc = gc


    def isMultiscaleJob(self, jobId):
        params = { "id" : jobId }
        try:
            resp = self.gc.get(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print("Error. invalid job id:", jobId)
                return False
            raise

        if not resp:
            return False

        metaData = resp.get('meta')

        if not isinstance(metaData, dict):
            return False

        if 'multiscale_settings' not in metaData:
            return False

        return True


    def getOutputFolderId(self, jobId):
        params = { "id" : jobId }
        try:
            resp = self.gc.get(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print("Error. invalid job id:", jobId)
                return
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

        return multiscale_settings['outputFolderId']


    def getOutputFolder(self, jobId):
        outputFolderId = self.getOutputFolderId(jobId)
        return self.gc.getFolder(outputFolderId)


    def downloadJobOutput(self, jobId):

        outputFolder = self.getOutputFolder(jobId)

        folderId = outputFolder.get('_id', 'id_unknown')
        folderName = outputFolder.get('name', 'name_unknown')

        self.gc.downloadFolderRecursive(folderId, folderName)

        print('Downloaded output to:', folderName)


    def runAlbanyJob(self, inputFolderId, outputFolderId):
        params = {
            "inputFolderId" : inputFolderId,
            "outputFolderId" : outputFolderId
        }
        return self.gc.post(MultiscaleUtils.RUN_ALBANY_PATH, parameters=params)
