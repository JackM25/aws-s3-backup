class Archive:
    """A zipped folder to be pushed to AWS"""

    def __init__(self, key, version, raw_size, date, location=None, size=0):
        self.key = key
        self.version = version
        self.raw_size = raw_size
        self.date = date
        self.location = location
        self.size = size

    def get_name(self):
        return self.key + '.' + self.version

    def update_size(self, size):
        self.size = size

    def update_location(self, location):
        self.location = location 