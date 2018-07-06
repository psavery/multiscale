import os

from girder.api import access
from girder.api.describe import Description, describeRoute, autoDescribeRoute
from girder.api.rest import (
    Resource,
    filtermodel,
    getCurrentUser,
    getApiUrl
)
from girder.models.upload import Upload
from girder.models.item import Item
from girder.models.token import Token
from girder.constants import AccessType

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import (
    HostStdOut,
    NamedOutputPipe,
    Connect,
    TemporaryVolume,
    VolumePath
)
from girder_worker.docker.transforms.girder import (
    GirderUploadVolumePathToItem,
    GirderFileIdToVolume,
    GirderFolderIdToVolume
)
from girder_worker.utils import JobStatus
from .utilities import wait_for_status

TEST_IMAGE = 'girder/girder_worker_test:ng'
ALBANY_IMAGE = 'psavery/albany'

class DockerTestEndpoints(Resource):
    def __init__(self):
        super(DockerTestEndpoints, self).__init__()
        self.route('POST', ('run_albany', ),
                   self.run_albany)
        self.route('POST', ('run_albany_from_girder_folder', ),
                   self.run_albany_from_girder_folder)
        self.route('POST', ('test_docker_run_file_upload_to_item', ),
                   self.test_docker_run_file_upload_to_item)
        self.route('POST', ('test_docker_run_girder_file_to_volume', ),
                   self.test_docker_run_girder_file_to_volume)
        self.route('POST', ('test_docker_run_cancel', ),
                   self.test_docker_run_cancel)

    @access.token
    @filtermodel(model='job', plugin='jobs')
    @autoDescribeRoute(
    Description('Run Albany on an input.yaml file')
    .param('workingDir', 'The path to the Albany working directory. "input.yaml" must be inside.',
           paramType='query', dataType='string', required='True'))
    def run_albany(self, params):
        workingDir = params.get('workingDir')
        filename = 'input.yaml'
        mount_dir = '/mnt/test'
        volumes = {
            workingDir : {
                'bind': mount_dir,
                'mode': 'rw'
            }
        }
        result = docker_run.delay(
            ALBANY_IMAGE, pull_image=False, container_args=[filename],
            entrypoint='/usr/local/albany/bin/AlbanyT', remove_container=True,
            volumes=volumes, working_dir=mount_dir)

        return result.job

    @access.token
    @filtermodel(model='job', plugin='jobs')
    @autoDescribeRoute(
    Description('Run Albany from a girder folder')
    .param('folderId', 'The id of the folder on girder. "input.yaml" must be inside.',
           paramType='query', dataType='string', required='True'))
    def run_albany_from_girder_folder(self, params):
        folderId = params.get('folderId')
        filename = 'input.yaml'
        volume = GirderFolderIdToVolume(folderId, volume=TemporaryVolume.default)
        result = docker_run.delay(
            ALBANY_IMAGE, pull_image=False, container_args=[filename],
            entrypoint='/usr/local/albany/bin/AlbanyT', remove_container=True,
            working_dir=volume)

        return result.job

    @access.token
    @filtermodel(model='job', plugin='jobs')
    @describeRoute(
        Description('Test uploading output file to item.'))
    def test_docker_run_file_upload_to_item(self, params):
        item_id = params.get('itemId')
        contents = params.get('contents')

        volumepath = VolumePath('test_file')

        result = docker_run.delay(
            TEST_IMAGE, pull_image=True,
            container_args=['write', '-p', volumepath, '-m', contents],
            remove_container=True,
            girder_result_hooks=[GirderUploadVolumePathToItem(volumepath, item_id)])

        return result.job


    @access.token
    @filtermodel(model='job', plugin='jobs')
    @describeRoute(
        Description('Test download to volume.'))
    def test_docker_run_girder_file_to_volume(self, params):
        file_id = params.get('fileId')

        result = docker_run.delay(
            TEST_IMAGE, pull_image=True,
            container_args=['read_write', '-i', GirderFileIdToVolume(file_id),
                            '-o', Connect(NamedOutputPipe('out'), HostStdOut())],
            remove_container=True)

        return result.job

    @access.token
    @filtermodel(model='job', plugin='jobs')
    @describeRoute(
        Description('Test cancel docker_run.'))
    def test_docker_run_cancel(self, params):
        mode = params.get('mode')
        result = docker_run.delay(
            TEST_IMAGE, pull_image=True, container_args=[mode],
            remove_container=True)

        assert wait_for_status(self.getCurrentUser(), result.job, JobStatus.RUNNING)
        result.revoke()

        return result.job
