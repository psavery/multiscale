"""Dream3D Pipeline Run.

On the girder server, run Dream3D's 'PipelineRunner'
executable on an input json file.
"""

from utilities.multiscale_utils import MultiscaleUtils

# Because we need the utilities folder...
import sys
sys.path.append('..')


def submitDream3DJob(gc, inputDir):
    """Run Dream3D's 'PipelineRunner' on a json file.

    gc should be an authenticated GirderClient object.
    inputDir is a local input directory that will be uploaded to
    the girder server.

    All output from dream3d should be saved in a directory called
    'output'.
    """
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

    job = mu.runDream3DJob(inputFolderId, outputFolderId)

    print('Job submitted:', job['_id'])
    print('Girder working directory:', baseFolderName + '/' + workingDirName)
