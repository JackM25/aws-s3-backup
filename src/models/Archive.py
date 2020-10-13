class Archive:
    """A Zipped up folder to be pushed to AWS"""

    def __init__(self, key, version, path, size, date, file):
        self.key = key
        self.version = version
        self.path = path
        self.size = size
        self.date = date
        self.file = file
