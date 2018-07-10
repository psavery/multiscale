"""Initialize the Multiscale end points."""

from .endpoints.multiscale import MultiscaleEndpoints


def load(info):
    """Load the end points."""
    info['apiRoot'].multiscale = MultiscaleEndpoints()
