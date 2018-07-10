#!/usr/bin/env python3


class UserUtils:

    ME_PATH = '/user/me'

    def __init__(self, gc):
        self.gc = gc

    def getCurrentUserId(self):
        resp = self.gc.get(UserUtils.ME_PATH)
        if resp and "_id" in resp:
            return resp["_id"]
        else:
            print("Warning: current user ID not found!")
            return None
