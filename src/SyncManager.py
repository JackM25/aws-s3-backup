class SyncManager:
    """Logic for detecting files to backup and then sending them to AWS"""

    def __init__(self, file_system, logger):
        self.logger = logger
        self.file_system = file_system
        self.logger.debug("Sync manager initialised")

    def run(self, data, dry_run):
        changes = []
        self.logger.info("Checking for changed files...")
        for a_file in self.file_system.files_to_sync(data):
            self.logger.info("Checking %s", a_file.get_path())

            file_changed, version = self.check_file_backup(a_file, data)
            if file_changed:
                changes.append({'file': a_file, 'version': version})
                self.logger.info("CHANGED: %s", a_file.get_path())
            else:
                self.logger.info("UNCHANGED: %s", a_file.get_path())

        if dry_run:
            self.log_files_to_backup(changes)
        else:
            self.backup_files(changes, data)

    def check_file_backup(self, a_file, data):
        """Check if we need to back up this file"""
        archive = data.latest_archive_for(a_file.key)
        if a_file.size != archive.raw_size:
            return (True, self.increment_version(archive.version))
        else:
            return (False, archive.version)

    def log_files_to_backup(self, changes):
        self.logger.info("")
        if len(changes) == 0:
            self.logger.info("No changes detected, 0 files will be backed up")
        else:
            self.logger.info(
                "The following files will be backed up:")
            for a_change in changes:
                self.logger.info("    %s will be updated to %s", a_change['file'].get_path(), a_change['version'])
            self.logger.info(
                "Run again without --dry-run to perfrom the backup")

    def backup_files(self, changes, data):
        self.logger.info("Starting sync...")
        file_count = 0
        for a_change in changes:
            self.logger.info("Syncing file %i of %i", file_count+1, len(changes))
            archive = self.file_system.create_zip_archive(a_change['file'], a_change['version'])
            # TODO: Push to AWS
            data.add_archive_to_state(archive)
            file_count += 1
        self.logger.info("Sync completed, backed up %i files", file_count)
        self.logger.info("Backup completed successfully")

    def increment_version(self, version):
        return 'v' + str(int(version[1:]) + 1)
