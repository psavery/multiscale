from .almech_endpoints import AlMechEndpoints

def load(info):
    info['apiRoot'].almech = AlMechEndpoints()
