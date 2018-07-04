from girder.models.model_base import AccessControlledModel

class AlMechModel(AccessControlledModel):
    def initialize(self):
        self.name = 'almech_model'
        self.ensureIndex('name')

    def validate(self, doc):
        return doc

    def run(self, doc):
        query = {
            '_id': doc['_id']
        }

        updates = {
            '$set': { 'ran': True }
        }

        print('An almech has ran!')
        return self.update(query, updates, multi=False)
