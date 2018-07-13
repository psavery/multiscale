"""End points for our multiscale operations."""

from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource, filtermodel

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import (
    TemporaryVolume,
    VolumePath
)
from girder_worker.docker.transforms.girder import (
    GirderUploadVolumePathToFolder,
    GirderFolderIdToVolume
)

from girder.plugins.jobs.models.job import Job

from . import utils

ALBANY_IMAGE = 'openchemistry/albany'
DREAM3D_IMAGE = 'openchemistry/dream3d'
SMTK_IMAGE = 'openchemistry/smtk'


class MultiscaleEndpoints(Resource):
    """End points for multiscale calculations."""

    def __init__(self):
        """Initialize the various routes."""
        super(MultiscaleEndpoints, self).__init__()
        self.route('POST', ('run_albany', ),
                   self.run_albany)
        self.route('POST', ('run_dream3d', ),
                   self.run_dream3d)
        self.route('POST', ('run_smtk_mesh_placement', ),
                   self.run_smtk_mesh_placement)

    @access.token
    @filtermodel(model=Job)
    @autoDescribeRoute(
        Description('Run Albany from a girder folder')
        .param('inputFolderId', 'The id of the input folder on girder.'
               '"input.yaml" must be inside, along with any other '
               'necessary input files. Will store the output in the '
               'specified output folder.',
               paramType='query', dataType='string', required='True')
        .param('outputFolderId', 'The id of the output folder on girder.',
               paramType='query', dataType='string', required='True'))
    def run_albany(self, params):
        """Run albany on a folder that is on girder.

        Will store the output in the specified output folder.
        """
        inputFolderId = params.get('inputFolderId')
        outputFolderId = params.get('outputFolderId')
        filename = 'input.yaml'
        folder_name = 'workingDir'
        volume = GirderFolderIdToVolume(
            inputFolderId,
            volume=TemporaryVolume.default,
            folder_name=folder_name)
        outputDir = inputFolderId + '/' + folder_name + '/output.exo'
        volumepath = VolumePath(outputDir, volume=TemporaryVolume.default)
        result = docker_run.delay(
            ALBANY_IMAGE, pull_image=False, container_args=[filename],
            entrypoint='/usr/local/albany/bin/AlbanyT', remove_container=True,
            working_dir=volume,
            girder_result_hooks=[
                GirderUploadVolumePathToFolder(volumepath, outputFolderId)
            ])

        # Set the multiscale meta data and return the job
        jobId = result.job['_id']
        return utils.setMultiscaleMetaData(jobId, inputFolderId,
                                           outputFolderId)

    @access.token
    @filtermodel(model=Job)
    @autoDescribeRoute(
        Description('Run Dream3D from a girder folder')
        .param('inputFolderId', 'The id of the input folder on girder.'
               '"input.json" must be inside, along with any other '
               'necessary input files. Note: all output must be saved '
               'in a directory called \'./output/\' - only files from this '
               'directory will be uploaded to the output folder on girder.',
               paramType='query', dataType='string', required='True')
        .param('outputFolderId', 'The id of the output folder on girder.',
               paramType='query', dataType='string', required='True'))
    def run_dream3d(self, params):
        """Run Dream3D on a folder that is on girder.

        Will store the output in the specified output folder.
        """
        inputFolderId = params.get('inputFolderId')
        outputFolderId = params.get('outputFolderId')
        filename = 'input.json'
        folder_name = 'workingDir'
        volume = GirderFolderIdToVolume(
            inputFolderId,
            volume=TemporaryVolume.default,
            folder_name=folder_name)
        outputDir = inputFolderId + '/' + folder_name + '/output'
        volumepath = VolumePath(outputDir, volume=TemporaryVolume.default)
        result = docker_run.delay(
            DREAM3D_IMAGE, pull_image=False, container_args=[filename],
            remove_container=True, working_dir=volume,
            girder_result_hooks=[
                GirderUploadVolumePathToFolder(volumepath, outputFolderId)
            ])

        # Set the multiscale meta data and return the job
        jobId = result.job['_id']
        return utils.setMultiscaleMetaData(jobId, inputFolderId,
                                           outputFolderId)

    @access.token
    @filtermodel(model=Job)
    @autoDescribeRoute(
        Description('Run smtk mesh placement from a girder folder')
        .param('inputFolderId', 'The id of the input folder on girder.'
               '"input.json" must be inside, along with any other '
               'necessary input files. Will store the output in the '
               'specified output folder.',
               paramType='query', dataType='string', required='True')
        .param('outputFolderId', 'The id of the output folder on girder.',
               paramType='query', dataType='string', required='True'))
    def run_smtk_mesh_placement(self, params):
        """Run an smtk mesh placement on a folder that is on girder.

        Will store the output in the specified output folder.
        """
        inputFolderId = params.get('inputFolderId')
        outputFolderId = params.get('outputFolderId')
        folder_name = 'workingDir'
        volume = GirderFolderIdToVolume(
            inputFolderId,
            volume=TemporaryVolume.default,
            folder_name=folder_name)
        outputDir = inputFolderId + '/' + folder_name + '/'
        volumepath = VolumePath(outputDir, volume=TemporaryVolume.default)
        result = docker_run.delay(
            SMTK_IMAGE,
            pull_image=False,
            container_args=[
                '-c',
                ('. ~/setupEnvironment; '
                 'python /usr/local/afrl-automation/runner.py input.json')],
            entrypoint='bash',
            remove_container=True,
            working_dir=volume,
            girder_result_hooks=[
                GirderUploadVolumePathToFolder(
                    volumepath,
                    outputFolderId)])

        # Set the multiscale meta data and return the job
        jobId = result.job['_id']
        return utils.setMultiscaleMetaData(jobId, inputFolderId,
                                           outputFolderId)
