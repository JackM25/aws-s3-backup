import os


class File:
    """A file or folder that should be considered for backup"""

    def __init__(self, key, entry, logger):
        self.key = key
        self.path = entry.path
        self.logger = logger
        if entry.is_dir():
            self.size = self.get_directory_size(entry.path)
        if entry.is_file():
            self.size = entry.stat().st_size

    def get_directory_size(self, dir):
        total = 0
        try:
            for entry in os.scandir(dir):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self.get_directory_size(entry.path)
        except NotADirectoryError:
            # if `directory` isn't a directory, get the file size then
            self.logger.error("Expected %s to be a directory", dir)
            return os.path.getsize(dir)
        except PermissionError:
            # if for whatever reason we can't open the folder, return 0
            self.logger.error("Permission error accessing %s", dir)
            return 0
        return total
