
# Because we need the utilities folder...
import sys
sys.path.append('..')

from utilities.multiscale_utils import MultiscaleUtils


def submitAlbanyCalculation(gc, inputDir):
    mu = MultiscaleUtils(gc)

    baseFolderName = MultiscaleUtils.BASE_FOLDER_NAME
    workingFolder = mu.createNewJobFolder()
    workingDirName = workingFolder['name']

    workingFolderId = workingFolder['_id']

    inputFolder = gc.createFolder(workingFolderId, 'input')
    outputFolder = gc.createFolder(workingFolderId, 'output')

    inputFolderId = inputFolder['_id']
    outputFolderId = outputFolder['_id']

    gc.upload(inputDir + '/*', inputFolderId)

    job = mu.runAlbanyJob(inputFolderId, outputFolderId)

    print('Job submitted:', job['_id'])
    print('Girder working directory:', baseFolderName + '/' + workingDirName)
