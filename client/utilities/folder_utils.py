#!/usr/bin/env python3


class FolderUtils:

    FOLDER_ID_PATH = '/folder/{id}'
    FOLDER_DELETE_PATH = FOLDER_ID_PATH

    def __init__(self, gc):
        self.gc = gc

    def getFolder(self, folderId):
        params = {'id': folderId}
        return self.gc.get(FolderUtils.FOLDER_ID_PATH, parameters=params)

    def getFolderName(self, folderId):
        return self.getFolder(folderId)['name']

    def getParentIdAndType(self, folderId):
        folder = self.getFolder(folderId)
        return folder['parentId'], folder['parentCollection']

    def getFullFolderPath(self, folderId):
        path = self.getFolderName(folderId)
        parentId, parentType = self.getParentIdAndType(folderId)

        while parentType == 'folder':
            path = self.getFolderName(parentId) + '/' + path
            parentId, parentType = self.getParentIdAndType(parentId)

        return path

    def deleteFolder(self, folderId):
        params = {'id': folderId}
        self.gc.delete(FolderUtils.FOLDER_DELETE_PATH, parameters=params)
