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
        self._logger = logger
        self._temp_dir = os.path.join(tempfile.gettempdir(), 'aws-s3-backup')

        if not os.path.exists(self._temp_dir):
            self._logger.debug(
                "Temp dir does not exists, creating at %s", self._temp_dir)
            os.makedirs(self._temp_dir)
        else:
            self._logger.debug("Using temp dir: %s", self._temp_dir)
        self._logger.debug("File system initialised")

    def files_to_sync(self, data):
        files = []
        self._logger.debug("Gathering files to check...")
        for backup_location in data.backup_locations():
            for entry in os.scandir(backup_location.path):
                if entry.is_symlink() or self._is_junction(entry.path):
                    self._logger.warn("Symlink not supported: %s", entry.path)
                    continue
                key = backup_location.key + '.' + \
                    (entry.name).replace(" ", "-").replace(".", "~")
                files.append(
                    File(key, self._get_size(entry), entry.name, entry.is_dir(), backup_location.path))

        return iter(files)

    def _get_size(self, entry):
        if entry.is_file():
            return entry.stat().st_size
        else:
            return self._get_directory_size(entry.path)

    def _get_directory_size(self, dir):
        total = 0
        try:
            for entry in os.scandir(dir):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self._get_directory_size(entry.path)
        except NotADirectoryError:
            # if directory isn't a directory, get the file size
            self._logger.error("Expected %s to be a directory", dir)
            return os.path.getsize(dir)
        except PermissionError:
            # if for whatever reason we can't open the folder, return 0
            self._logger.error("Permission error accessing %s", dir)
            return 0
        return total

    def _is_junction(self, dir):
        try:
            return os.readlink(dir)
        except OSError:
            return False

    def create_zip_archive(self, file, version):
        self._logger.info("Creating zip archive for %s", file.name)
        archive = Archive(file.key, version, file.size, datetime.now())

        if file.is_dir:
            self._logger.debug("Zipping folder")
            archive_path = shutil.make_archive(os.path.join(
                self._temp_dir, archive.get_name()), archive.extension, file.get_path())
        else:
            self._logger.debug("Zipping file")
            archive_path = shutil.make_archive(os.path.join(
                self._temp_dir, archive.get_name()), archive.extension, file.parent_dir, file.name)

        archive_size = Path(archive_path).stat().st_size
        archive.update_location(archive_path)
        archive.update_size(archive_size)
        self._logger.debug("Zip archive created")

        return archive

    def empty_temp_folder(self):
        self._logger.debug("Emptying temp directory: %s", self._temp_dir)
        for root, dirs, files in os.walk(self._temp_dir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
