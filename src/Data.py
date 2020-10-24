import json
from datetime import datetime
from src.models.BackupLocation import BackupLocation
from src.models.Archive import Archive


class Data:
    """Wrapper around the data file"""

    def __init__(self, file_location, logger):
        self._file_location = file_location
        self._logger = logger

        self._logger.info('Loading data file from %s', file_location)
        f = open(file_location)
        self._logger.debug('Parsing data file...')
        self._data = json.load(f)
        f.close()
        self._logger.debug('Data file loaded')
        self._logger.debug("Data manager initialised")

    def properties(self):
        return self._data['properties']

    def state(self):
        return self._data['state']

    def aws_access_key(self):
        return self.properties()['aws']['access_key']

    def aws_secret_key(self):
        return self.properties()['aws']['secret_key']

    def aws_bucket(self):
        return self.properties()['aws']['bucket']

    def aws_storage_class(self):
        return self.properties()['aws']['storage_class']

    def backup_locations(self):
        locations = []
        self._logger.debug("Reading backup locations from data file")
        for location in self.properties()['backup_locations']:
            locations.append(BackupLocation(location['key'], location['path']))
        return locations

    def latest_archive_for(self, key):
        self._logger.debug(
            "Retrieving latest archive for %s from data file", key)
        if self.state():
            if key in self.state():
                all_states = self.state()[key]
                latest_version = max(list(all_states.keys()))
                return Archive(
                    key,
                    latest_version,
                    self.state()[key][latest_version]['raw_size'],
                    datetime.fromisoformat(
                        self.state()[key][latest_version]['date']),
                    self.state()[key][latest_version]['location'],
                    self.state()[key][latest_version]['size'],
                )
        self._logger.debug("No archive found, returning empty archive")
        return Archive(key, 'v0', 0, None)

    def add_archive_to_state(self, archive):
        self._logger.debug('Adding %s to state', archive.get_name())

        if not archive.key in self.state():
            self.state()[archive.key] = {}

        self.state()[archive.key][archive.version] = {
            'name': archive.get_name(),
            'size': archive.size,
            'date': archive.date.isoformat(),
            'location': archive.location,
            'raw_size': archive.raw_size,
        }
        self._write_state_to_file()

    def _write_state_to_file(self):
        self._logger.debug('Writing state to disk...')
        f = open(self._file_location, 'w')
        json.dump(self._data, f, ensure_ascii=False, indent=4)
        f.close()
        self._logger.debug('State saved')
