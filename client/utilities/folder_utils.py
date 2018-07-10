"""Folder utility functions for communicating with girder."""


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
