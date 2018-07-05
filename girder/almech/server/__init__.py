from girder.api import access
from girder.constants import AccessType, registerAccessFlag
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource

from girder.plugins.almech.models.almech_model import AlMechModel

class AlMechResource(Resource):
    def __init__(self):
        super(AlMechResource, self).__init__()
        self.resourceName = 'almech'

        self.route('GET', (), self.findAlMech)
        self.route('GET', (':id',), self.getAlMech)
        self.route('POST', (), self.createAlMech)
        self.route('PUT', (':id',), self.updateAlMech)
        self.route('DELETE', (':id',), self.deleteAlMech)
        self.route('PUT', (':id', 'run'), self.runAlMech)

    @access.public
    @autoDescribeRoute(
    Description('Find an almech'))
    def findAlMech(self, params):
        print('findAlMech() was called!')
        print('params is', params)

    @access.public
    @autoDescribeRoute(
    Description('Get an almech')
    .modelParam('id', 'The almech ID', model=AlMechModel, level=AccessType.READ,
                destName='doc'))
    def getAlMech(self, doc, params):
        print('getAlMech() was called!')
        print('doc is', doc)
        print('params is', params)
        return doc

    @access.public
    @autoDescribeRoute(
    Description('Create a almech'))
    def createAlMech(self, params):
        document = {}
        alMechModel = AlMechModel().save(document)
        return alMechModel

    @access.public
    @autoDescribeRoute(
    Description('Update a almech')
    .modelParam('id', 'The almech ID', model=AlMechModel, level=AccessType.WRITE))
    def updateAlMech(self, params):
        print("params is", params)
        if 'almech_model' not in params:
            print("Error: no almech model in the parameter!")
            return

        alMechModel = params['almech_model']
        if '_id' not in alMechModel:
            print("Error: missing id from alMechModel!")
            return

        id = alMechModel['_id']

        print("id is", id)
        print('updateAlMech() was called!')

    @access.public
    @autoDescribeRoute(
    Description('Delete a almech')
    .modelParam('id', 'The almech ID', model=AlMechModel, level=AccessType.WRITE,
                destName='doc'))
    def deleteAlMech(self, doc, params):
        print('doc is', doc)
        print('params is', params)
        print('deleteAlMech() was called!')
        AlMechModel().remove(doc)

    registerAccessFlag(key='almech.run', name='Run an almech simulation',
                       description='Allows users to run an almech simulation')

    @access.user
    @autoDescribeRoute(
    Description('Run an almech simulation')
    .modelParam('id', 'The almech ID', model=AlMechModel, plugin='almech',
                 level=AccessType.WRITE, requiredFlags='almech.run',
                 destName='doc'))
    def runAlMech(self, doc, params):
        print('doc is', doc)
        print('params is', params)

        # Run the almech
        return AlMechModel().run(doc)


def load(info):
    info['apiRoot'].almech = AlMechResource()
