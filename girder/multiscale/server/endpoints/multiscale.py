"""End points for our multiscale operations."""

from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource, filtermodel

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import (
    BindMountVolume,
    TemporaryVolume,
    VolumePath
)
from girder_worker.docker.transforms.girder import (
    GirderUploadVolumePathToFolder,
    GirderFolderIdToVolume
)

from girder.plugins.jobs.models.job import Job

ALBANY_IMAGE = 'openchemistry/albany'


class MultiscaleEndpoints(Resource):
    """End points for multiscale calculations."""

    def __init__(self):
        """Initialize the various routes."""
        super(MultiscaleEndpoints, self).__init__()
        self.route('POST', ('run_albany_local', ),
                   self.run_albany_local)
        self.route('POST', ('run_albany_from_girder_folder', ),
                   self.run_albany_from_girder_folder)

    @access.token
    @filtermodel(model=Job)
    @autoDescribeRoute(
        Description('Run Albany on an input.yaml file already on the server')
        .param('workingDir', 'The path to the Albany working directory. '
               '"input.yaml" must be inside.',
               paramType='query', dataType='string', required='True'))
    def run_albany_local(self, params):
        """Run albany on an input.yaml file already on the server."""
        workingDir = params.get('workingDir')
        filename = 'input.yaml'
        mount_dir = '/mnt/test'
        vol = BindMountVolume(workingDir, mount_dir)
        result = docker_run.delay(
            ALBANY_IMAGE, pull_image=False, container_args=[filename],
            entrypoint='/usr/local/albany/bin/AlbanyT', remove_container=True,
            volumes=[vol], working_dir=mount_dir)

        return result.job

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
    def run_albany_from_girder_folder(self, params):
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

        # We want to update the job with some multiscale settings.
        # We will put it in the meta data.
        job = Job().findOne({'_id': result.job['_id']})
        multiscale_io = {
            'meta': {
                'multiscale_settings': {
                    'inputFolderId': inputFolderId,
                    'outputFolderId': outputFolderId
                }
            }
        }

        return Job().updateJob(job, otherFields=multiscale_io)
