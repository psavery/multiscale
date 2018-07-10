#!/usr/bin/env python3

from girder_client import HttpError

from .job_utils import JobUtils
from .user_utils import UserUtils

class MultiscaleUtils:

    RUN_ALBANY_PATH = '/multiscale/run_albany_from_girder_folder'

    BASE_FOLDER_NAME = 'multiscale_data'
    MAX_JOBS = 10000

    def __init__(self, gc):
        self.gc = gc


    def getBaseFolder(self):
        uu = UserUtils(self.gc)
        userId = uu.getCurrentUserId()
        return self.gc.createFolder(
            userId, MultiscaleUtils.BASE_FOLDER_NAME,
            description='Data for multiscale calculations',
            parentType='user', reuseExisting=True,
            public=False)


    def createNewJobFolder(self):
        baseFolder = self.getBaseFolder()
        baseFolderId = baseFolder['_id']

        folderNames = []
        for folder in self.gc.listFolder(baseFolderId):
            folderNames.append(folder['name'])

        baseName = 'job_'
        workingDirName = ''
        for i in range(1, MultiscaleUtils.MAX_JOBS + 1):
            tmpName = baseName + str(i)
            if tmpName not in folderNames:
                workingDirName = tmpName
                break

        if not workingDirName:
            print("Error: the maximum number of jobs has been exceeded.",
                  "\nPlease delete some jobs in your folder.")
            return

        return self.gc.createFolder(baseFolderId, workingDirName)


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
