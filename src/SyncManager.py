class SyncManager:
    """Logic for detecting files to backup and then sending them to AWS"""

    def __init__(self, file_system, aws, logger):
        self._file_system = file_system
        self._aws = aws
        self._logger = logger
        self._logger.debug("Sync manager initialised")

    def run(self, data, dry_run):
        changes = []
        self._logger.info("Checking for changed files...")
        for a_file in self._file_system.files_to_sync(data):
            self._logger.info("Checking %s", a_file.get_path())

            file_changed, version = self._check_file_needs_backup(a_file, data)
            if file_changed:
                changes.append({'file': a_file, 'version': version})
                self._logger.info("CHANGED: %s", a_file.get_path())
            else:
                self._logger.info("UNCHANGED: %s", a_file.get_path())

        if dry_run:
            self._log_files_to_backup(changes)
        else:
            self._backup_files(changes, data)

    def _check_file_needs_backup(self, a_file, data):
        """Check if we need to back up this file"""
        archive = data.latest_archive_for(a_file.key)
        if a_file.size != archive.raw_size:
            return (True, self._increment_version(archive.version))
        else:
            return (False, archive.version)

    def _log_files_to_backup(self, changes):
        self._logger.info("")
        if len(changes) == 0:
            self._logger.info("No changes detected, 0 files will be backed up")
        else:
            self._logger.info(
                "The following files will be backed up:")
            for a_change in changes:
                self._logger.info("    %s will be updated to %s",
                                 a_change['file'].get_path(), a_change['version'])
            self._logger.info(
                "Run again without --dry-run to perfrom the backup")

    def _backup_files(self, changes, data):
        self._logger.info("Starting sync...")
        file_count = 0
        file_success_count = 0

        for a_change in changes:
            self._logger.info("Syncing file %i of %i",
                             file_count+1, len(changes))
            archive = self._file_system.create_zip_archive(
                a_change['file'], a_change['version'])
            upload_result = self._aws.upload_archive(archive)

            if upload_result:
                data.add_archive_to_state(archive)
                file_count += 1
                file_success_count +=1
                self._logger.info("File synced")
            else:
                file_count += 1
                self._logger.error("File sync failed, %s has not been uploaded", archive.get_name())
                self._logger.error("Run this process again to try again")

        self._logger.info("Sync completed, backed up %i files", file_success_count)
        if file_count - file_success_count > 0:
            self._logger.error("%i files could not be backed up", file_count - file_success_count)

        self._file_system.empty_temp_folder()
        self._logger.info("Backup completed successfully")

    def _increment_version(self, version):
        return 'v' + str(int(version[1:]) + 1)
