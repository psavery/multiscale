from .endpoints.multiscale import MultiscaleEndpoints


def load(info):
    info['apiRoot'].multiscale = MultiscaleEndpoints()
