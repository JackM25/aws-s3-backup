class BackupLocation:
    """A folder for whose content should be backed"""

    def __init__(self, key, path):
        self.key = key
        self.path = path

    @classmethod
    def from_dict(cls, dict):
        return cls(dict['key'], dict['path'])
