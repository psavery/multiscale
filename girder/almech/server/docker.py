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
    VolumePath
)
from girder_worker.docker.transforms.girder import (
    GirderUploadVolumePathToItem,
    GirderFileIdToVolume
)
from girder_worker.utils import JobStatus
from .utilities import wait_for_status

TEST_IMAGE = 'girder/girder_worker_test:ng'


class DockerTestEndpoints(Resource):
    def __init__(self):
        super(DockerTestEndpoints, self).__init__()
        self.route('POST', ('test_docker_run', ),
                   self.test_docker_run)
        self.route('POST', ('test_docker_run_mount_volume', ),
                   self.test_docker_run_mount_volume)
        self.route('POST', ('test_docker_run_file_upload_to_item', ),
                   self.test_docker_run_file_upload_to_item)
        self.route('POST', ('test_docker_run_girder_file_to_volume', ),
                   self.test_docker_run_girder_file_to_volume)
        self.route('POST', ('test_docker_run_raises_exception', ),
                   self.test_docker_run_raises_exception)
        self.route('POST', ('test_docker_run_cancel', ),
                   self.test_docker_run_cancel)

    @access.token
    @filtermodel(model='job', plugin='jobs')
    @describeRoute(
        Description('Test basic docker_run.'))
    def test_docker_run(self, params):
        result = docker_run.delay(
            TEST_IMAGE, pull_image=True, container_args=['stdio', '-m', 'hello docker!'],
            remove_container=True)

        return result.job

    @access.token
    @filtermodel(model='job', plugin='jobs')
    @describeRoute(
        Description('Test docker run that raises an exception.'))
    def test_docker_run_raises_exception(self, params):
        result = docker_run.delay(
            TEST_IMAGE, pull_image=True, container_args=['raise_exception'], remove_container=True)
        return result.job

    @access.token
    @filtermodel(model='job', plugin='jobs')
    @describeRoute(
        Description('Test mounting a volume.'))
    def test_docker_run_mount_volume(self, params):
        fixture_dir = params.get('fixtureDir')
        filename = 'read.txt'
        mount_dir = '/mnt/test'
        mount_path = os.path.join(mount_dir, filename)
        volumes = {
            fixture_dir: {
                'bind': mount_dir,
                'mode': 'ro'
            }
        }
        result = docker_run.delay(
            TEST_IMAGE, pull_image=True, container_args=['read', '-p', mount_path],
            remove_container=True, volumes=volumes)

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
