
import sys
sys.path.append("..")

from utilities.multiscale_utils import MultiscaleUtils
from utilities.user_utils import UserUtils

MAX_JOBS = 10000

def submitAlbanyCalculation(gc, inputDir):
    mu = MultiscaleUtils(gc)
    uu = UserUtils(gc)
    userId = uu.getCurrentUserId()

    baseFolderName = 'multiscale_data'
    baseFolder = gc.createFolder(userId, baseFolderName,
                                 description='Data for multiscale calculations',
                                 parentType='user', reuseExisting=True,
                                 public=False)

    baseFolderId = baseFolder['_id']

    folderNames = []
    for folder in gc.listFolder(baseFolderId):
        folderNames.append(folder['name'])

    baseName = 'job_'
    for i in range(1, MAX_JOBS + 1):
        workingDirName = baseName + str(i)
        if workingDirName in folderNames:
            continue

        break

    workingFolder = gc.createFolder(baseFolderId, workingDirName)

    workingFolderId = workingFolder['_id']

    inputFolder = gc.createFolder(workingFolderId, 'input')
    outputFolder = gc.createFolder(workingFolderId, 'output')

    inputFolderId = inputFolder['_id']
    outputFolderId = outputFolder['_id']

    gc.upload(inputDir + '/*', inputFolderId)

    job = mu.runAlbanyJob(inputFolderId, outputFolderId)

    print("Job submitted:", job['_id'])
    print("Girder working directory:", baseFolderName + '/' + workingDirName)
