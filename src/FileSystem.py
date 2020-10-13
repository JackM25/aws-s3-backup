import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from src.models.File import File
from src.models.Archive import Archive


class FileSystem:
    """Logic for interfacing with the file system"""

    def __init__(self, logger):
        self.logger = logger
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'aws-s3-backup')
        if not os.path.exists(self.temp_dir):
            self.logger.debug("Temp dir does not exists, creating at %s", self.temp_dir)
            os.makedirs(self.temp_dir)
        else:
            self.logger.debug("Using temp dir: %s", self.temp_dir)


    def files_to_sync(self, data):
        files = []
        for backup_location in data.backup_locations():
            for entry in os.scandir(backup_location.path):
                if entry.is_symlink() or self.is_junction(entry.path):
                    self.logger.warn("Symlink not supported: %s", entry.path)
                    continue
                key = backup_location.key + '.' + \
                    (entry.name).replace(" ", "-").replace(".", "~")
                files.append(File(key, entry, backup_location.path, self.logger))
        return iter(files)

    def is_junction(self, dir):
        try:
            return os.readlink(dir)
        except OSError:
            return False

    def create_zip_archive(self, file):
        if file.is_dir:
            archive_path = shutil.make_archive(os.path.join(self.temp_dir, (file.key + '.' + file.version)), 'zip', file.path)
        else:
            archive_path = shutil.make_archive(os.path.join(self.temp_dir, (file.key + '.' + file.version)), 'zip', file.parent_dir, file.name)
        zip_size = Path(archive_path).stat().st_size
        return Archive(file.key, file.version, archive_path, zip_size, datetime.now(), file)
