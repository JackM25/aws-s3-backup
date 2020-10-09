from datetime import datetime

class FileState:
    """State of a backed up file"""

    def __init__(self, key, version, size = 0, date = datetime(1970, 1, 1, 0, 0, 0, 0)):
        self.key = key
        self.version = version
        self.size = size
        self.date = date

    @classmethod
    def from_dict(cls, key, version, dict):
        return cls(key, version, dict['size'], dict['date'])
