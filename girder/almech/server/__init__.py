from .endpoints.almech import AlMechEndpoints

def load(info):
    info['apiRoot'].almech = AlMechEndpoints()
