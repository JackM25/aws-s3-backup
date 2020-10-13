from src.models.FileState import FileState

class SyncManager:
    """Logic for detecting files to backup and then sending them to AWS"""

    def __init__(self, file_system, logger):
        self.logger = logger
        self.file_system = file_system
        logger.debug("Sync manager initialised")

    def run(self, data, dry_run):
        files_to_backup = []
        for a_file in self.file_system.files_to_sync(data):
            self.logger.info("Checking %s", a_file.path)
            if self.file_changed(a_file, data):
                files_to_backup.append(a_file)
                self.logger.info("CHANGED: %s", a_file.path)
            else:
                self.logger.info("UNCHANGED: %s", a_file.path)
        if dry_run:
            self.log_files_to_backup(files_to_backup)
        else:
            self.backup_files(files_to_backup, data)

    def log_files_to_backup(self, files):
        self.logger.info("")
        self.logger.info(
            "The following files will be backed up:")
        for a_file in files:
            self.logger.info("    %s", a_file.path)
        self.logger.info("Run again without --dry-run to perfrom the backup")

    def file_changed(self, a_file, data):
        """Return true if we have never backed up this file, or it has been changed since the last backup"""
        state = data.latest_state_for(a_file.key)
        if a_file.size != state.size:
            a_file.set_version(state.get_next_version())
            return True
        else:
            a_file.set_version(state.version)
            return False

    def backup_files(self, files, data):
        self.logger.info("Starting sync...")
        for a_file in files:
            archive = self.file_system.create_zip_archive(a_file)
            # TODO: Push to AWS
            data.add_file_state(FileState.from_archive(archive))
