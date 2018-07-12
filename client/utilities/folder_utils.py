"""Folder utility functions for communicating with girder."""

import os

class FolderUtils:
    """Utility functions for performing folder operations on girder."""

    FOLDER_ID_PATH = '/folder/{id}'
    FOLDER_DELETE_PATH = FOLDER_ID_PATH

    def __init__(self, gc):
        """Initialize with an authenticated GirderClient object."""
        self.gc = gc

    def getFolder(self, folderId):
        """Get a folder from a folderId."""
        params = {'id': folderId}
        return self.gc.get(FolderUtils.FOLDER_ID_PATH, parameters=params)

    def getFolderName(self, folderId):
        """Get a folder name from a folderId."""
        return self.getFolder(folderId)['name']

    def getParentIdAndType(self, folderId):
        """Get the parent ID and type from a folderId."""
        folder = self.getFolder(folderId)
        return folder['parentId'], folder['parentCollection']

    def getFullFolderPath(self, folderId):
        """Get the full folder path on the girder server.

        For example: multiscale_data/job_1
        """
        path = self.getFolderName(folderId)
        parentId, parentType = self.getParentIdAndType(folderId)

        while parentType == 'folder':
            path = self.getFolderName(parentId) + '/' + path
            parentId, parentType = self.getParentIdAndType(parentId)

        return path

    def deleteFolder(self, folderId):
        """Delete a folder given its folderId."""
        params = {'id': folderId}
        self.gc.delete(FolderUtils.FOLDER_DELETE_PATH, parameters=params)

    @staticmethod
    def getUniqueLocalFolderName(folder):
        """Get a unique local folder name with 'folder' as the base.

        If 'folder' does not exist, this method returns 'folder'.
        If 'folder' does exist, it will try 'folder'_1, then 'folder'_2,
        etc., and it will return the first folder that does not already
        exist on the local file system.
        """
        baseName = folder
        counter = 1
        while os.path.isdir(folder) or os.path.isfile(folder):
            folder = baseName + '_' + str(counter)
            counter += 1

        return folder
