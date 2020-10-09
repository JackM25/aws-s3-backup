class SyncManager:
    """Logic for detecting files to backup and then sending them to AWS"""

    def __init__(self, file_system, logger):
        self.logger = logger
        self.file_system = file_system
        logger.debug("Sync manager initialised")

    def run(self, data, dry_run):
        # Loop over all results from file system
        # If changed
        # if dry run just log
        # else
        # FS create a zip
        # push to AWS
        # update data file
        # else log not changed
        files_to_backup = []
        for a_file in self.file_system.files_to_sync(data):
            self.logger.info("Checking %s", a_file.path)
            if self.file_changed(a_file, data):
                files_to_backup.append(a_file)
                self.logger.info("CHANGED: %s", a_file.path)
            else:
                self.logger.info("UNCHANGED: %s", a_file.path)

    def file_changed(self, a_file, data):
        """Return true if we have never backed up this file, or it has been changed since the last backup"""
        state = data.latest_state_for(a_file.key)
        if a_file.size != state.size:
            return True
        else:
            return False
