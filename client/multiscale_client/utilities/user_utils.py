"""User utility functions for communicating with girder."""

# Python2 and python3 compatibility
from __future__ import print_function


class UserUtils:
    """Utility functions for performing user operations on girder."""

    ME_PATH = '/user/me'

    def __init__(self, gc):
        """Initialize with an authenticated GirderClient object."""
        self.gc = gc

    def getCurrentUserId(self):
        """Get the current user's id number."""
        resp = self.gc.get(UserUtils.ME_PATH)
        if resp and '_id' in resp:
            return resp['_id']
        else:
            print('Warning: current user ID not found!')
            return None
