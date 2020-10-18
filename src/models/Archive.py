class Archive:
    """A zipped folder to be or that has been pushed to AWS"""

    def __init__(self, key, version, raw_size, date, location=None, size=0):
        self.key = key
        self.version = version
        self.raw_size = raw_size
        self.date = date
        self.location = location
        self.size = size
        self.extension = 'zip'

    def get_name(self):
        return self.key + '.' + self.version

    def get_file_name(self):
        return self.key + '.' + self.version + '.' + self.extension

    def update_size(self, size):
        self.size = size

    def update_location(self, location):
        self.location = location
