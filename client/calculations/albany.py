"""Albany Calculation.

On the girder server, run an Albany calculation with a given
Albany input.
"""

# Python2 and python3 compatibility
from __future__ import print_function

from utilities.multiscale_utils import MultiscaleUtils

# Because we need the utilities folder...
import sys
sys.path.append('..')


def submitAlbanyCalculation(gc, inputDir):
    """Submit an albany calculation on the girder server.

    gc should be an authenticated GirderClient object.
    inputDir is a local input directory that will be uploaded to
    the girder server.
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

    job = mu.runAlbanyJob(inputFolderId, outputFolderId)

    print('Job submitted:', job['_id'])
    print('Girder working directory:', baseFolderName + '/' + workingDirName)
