"""Multiscale utility functions for communicating with girder."""

from girder_client import HttpError

from .folder_utils import FolderUtils
from .job_utils import JobUtils
from .user_utils import UserUtils


class MultiscaleUtils:
    """Utility functions for performing multiscale operations on girder."""

    RUN_ALBANY_PATH = '/multiscale/run_albany_from_girder_folder'

    BASE_FOLDER_NAME = 'multiscale_data'
    MAX_JOBS = 10000

    def __init__(self, gc):
        """Initialize with an authenticated GirderClient object."""
        self.gc = gc

    def getBaseFolder(self):
        """Get the base folder for multiscale data on girder."""
        uu = UserUtils(self.gc)
        userId = uu.getCurrentUserId()
        return self.gc.createFolder(
            userId, MultiscaleUtils.BASE_FOLDER_NAME,
            description='Data for multiscale calculations',
            parentType='user', reuseExisting=True,
            public=False)

    def createNewJobFolder(self):
        """Create a new job folder for a calculation on girder.

        Returns the new folder.
        """
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
            print('Error: the maximum number of jobs has been exceeded.',
                  '\nPlease delete some jobs in your folder.')
            return

        return self.gc.createFolder(baseFolderId, workingDirName)

    def isMultiscaleJob(self, jobId):
        """Check to see if the given jobId is for a multiscale job."""
        params = {'id': jobId}
        try:
            resp = self.gc.get(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print('Error. invalid job id:', jobId)
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

    def getInputOrOutputFolderId(self, jobId, folderType):
        """Get the input or output folder for a specified jobId.

        The folderType must be "input" or "output"
        """
        params = {'id': jobId}
        try:
            resp = self.gc.get(JobUtils.JOB_ID_PATH, parameters=params)
        except HttpError as e:
            if e.status == 400:
                print('Error. invalid job id:', jobId)
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

        folderIdName = ''
        if folderType == 'input':
            folderIdName = 'inputFolderId'
        elif folderType == 'output':
            folderIdName = 'outputFolderId'
        else:
            print('Error: unknown folder type:', folderType)
            return

        if folderIdName not in multiscale_settings:
            print('Error:', folderIdName, 'is not in multiscale_settings!')
            return

        return multiscale_settings[folderIdName]

    def getInputFolderId(self, jobId):
        """Get the input folder id for a multiscale job."""
        return self.getInputOrOutputFolderId(jobId, 'input')

    def getOutputFolderId(self, jobId):
        """Get the output folder id for a multiscale job."""
        return self.getInputOrOutputFolderId(jobId, 'output')

    def getJobFolderId(self, jobId):
        """Get the job folder id for a specified job.

        This function will check to see if the parent folder of the
        output folder appears to be a job folder. If it is, it will
        return the parent folderid.

        If the parent is not a job folder, the function will return
        the folder for the job output.
        """
        outputFolderId = self.getOutputFolderId(jobId)

        fu = FolderUtils(self.gc)
        folder = fu.getFolder(outputFolderId)

        parentId = folder['parentId']
        parentType = folder['parentCollection']

        # If the parent is not a folder, do not return it
        if parentType != 'folder':
            return outputFolderId

        parentFolder = fu.getFolder(parentId)
        parentName = parentFolder['name']
        # Double check and make sure the parent name starts with 'job_'
        if not parentName.startswith('job_'):
            return outputFolderId

        return parentId

    def getInputFolder(self, jobId):
        """Get the input folder for a specified job id."""
        inputFolderId = self.getInputFolderId(jobId)
        return self.gc.getFolder(inputFolderId)

    def getOutputFolder(self, jobId):
        """Get the output folder for a specified job id."""
        outputFolderId = self.getOutputFolderId(jobId)
        return self.gc.getFolder(outputFolderId)

    def downloadJobInput(self, jobId):
        """Download the job input folder for a specified job id."""
        inputFolder = self.getInputFolder(jobId)

        folderId = inputFolder.get('_id', 'id_unknown')
        folderName = inputFolder.get('name', 'name_unknown')

        self.gc.downloadFolderRecursive(folderId, folderName)

        print('Downloaded input to:', folderName)

    def downloadJobOutput(self, jobId):
        """Download the job output folder for a specified job id."""
        outputFolder = self.getOutputFolder(jobId)

        folderId = outputFolder.get('_id', 'id_unknown')
        folderName = outputFolder.get('name', 'name_unknown')

        self.gc.downloadFolderRecursive(folderId, folderName)

        print('Downloaded output to:', folderName)

    def runAlbanyJob(self, inputFolderId, outputFolderId):
        """Run an albany job on the girder server.

        inputFolderId is the ID of the input folder.
        outputFolderId is the ID of the output folder.

        After albany completes, the output will be sent to
        the outputFolder.
        """
        params = {
            'inputFolderId': inputFolderId,
            'outputFolderId': outputFolderId
        }
        return self.gc.post(MultiscaleUtils.RUN_ALBANY_PATH, parameters=params)
