class BackupLocation:
    """A folder for whose content should be backed"""

    def __init__(self, key, path):
        self.key = key
        self.path = path
