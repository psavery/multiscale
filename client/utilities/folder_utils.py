#!/usr/bin/env python3

from girder_client import HttpError

class FolderUtils:

    FOLDER_ID_PATH = '/folder/{id}'
    FOLDER_DELETE_PATH = FOLDER_ID_PATH


    def __init__(self, gc):
        self.gc = gc


    def getFolderName(self, folderId):
        params = { "id" : folderId }
        folder = self.gc.get(FolderUtils.FOLDER_ID_PATH, parameters=params)
        return folder['name']


    def getParentIdAndType(self, folderId):
        params = { "id" : folderId }
        folder = self.gc.get(FolderUtils.FOLDER_ID_PATH, parameters=params)
        return folder['parentId'], folder['parentCollection']


    def getFullFolderPath(self, folderId):
        path = self.getFolderName(folderId)
        parentId, parentType = self.getParentIdAndType(folderId)

        while parentType == 'folder':
            path = self.getFolderName(parentId) + '/' + path
            parentId, parentType = self.getParentIdAndType(parentId)

        return path


    def deleteFolder(self, folderId):
        params = { "id" : folderId }
        self.gc.delete(FolderUtils.FOLDER_DELETE_PATH, parameters=params)
