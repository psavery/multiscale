
# Because we need the utilities folder...
import sys
sys.path.append("..")

from utilities.multiscale_utils import MultiscaleUtils

MAX_JOBS = 10000

def submitAlbanyCalculation(gc, inputDir):
    mu = MultiscaleUtils(gc)

    baseFolderName = MultiscaleUtils.BASE_FOLDER_NAME
    baseFolder = mu.getBaseFolder()
    baseFolderId = baseFolder['_id']

    folderNames = []
    for folder in gc.listFolder(baseFolderId):
        folderNames.append(folder['name'])

    baseName = 'job_'
    for i in range(1, MAX_JOBS + 1):
        workingDirName = baseName + str(i)
        if workingDirName not in folderNames:
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
