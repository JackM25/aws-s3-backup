import json
from datetime import datetime
from src.models.BackupLocation import BackupLocation
from src.models.Archive import Archive


class Data:
    """Wrapper around the data file"""

    def __init__(self, file_location, logger):
        self.file_location = file_location
        self.logger = logger
        self.logger.info('Loading data file from %s', file_location)
        f = open(file_location)
        self.logger.debug('Parsing data file...')
        self.data = json.load(f)
        f.close()
        self.logger.debug('Data file loaded')
        self.logger.debug("Data manager initialised")

    def properties(self):
        return self.data['properties']

    def state(self):
        return self.data['state']

    def backup_locations(self):
        locations = []
        self.logger.debug("Reading backup locations from data file")
        for location in self.properties()['backup_locations']:
            locations.append(BackupLocation(location['key'], location['path']))
        return locations

    def latest_archive_for(self, key):
        self.logger.debug("Retrieving latest archive for %s from data file", key)
        if self.state():
            if self.state()[key]:
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
        self.logger.debug("No archive found, returning empty archive")
        return Archive(key, 'v0', 0, None)

    def add_archive_to_state(self, archive):
        self.logger.debug('Adding %s to state', archive.get_name())

        if not archive.key in self.state():
            self.state()[archive.key] = {}

        self.state()[archive.key][archive.version] = {
            'name': archive.get_name(),
            'size': archive.size,
            'date': archive.date.isoformat(),
            'location': archive.location,
            'raw_size': archive.raw_size,
        }
        self.write_state_to_file()

    def write_state_to_file(self):
        self.logger.debug('Writing state to disk...')
        f = open(self.file_location, 'w')
        json.dump(self.data, f, ensure_ascii=False, indent=4)
        f.close()
        self.logger.debug('State saved')
