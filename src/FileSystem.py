import os
from src.models.File import File


class FileSystem:
    """Logic for interfacing with the file system"""

    def __init__(self, logger):
        self.logger = logger

    def files_to_sync(self, data):
        files = []
        for backup_location in data.backup_locations():
            for entry in os.scandir(backup_location.path):
                if entry.is_symlink() or self.is_junction(entry.path):
                    self.logger.warn("Symlink not supported: %s", entry.path)
                    continue
                key = backup_location.key + '.' + \
                    (entry.name).replace(" ", "-").replace(".", "~")
                files.append(File(key, entry, self.logger))
        return iter(files)

    def is_junction(self, dir):
        try:
            return os.readlink(dir)
        except OSError:
            return False
