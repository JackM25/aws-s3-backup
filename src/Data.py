import json
from src.models.BackupLocation import BackupLocation
from src.models.FileState import FileState


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

    def properties(self):
        return self.data['properties']

    def state(self):
        return self.data['state']

    def backup_locations(self):
        locations = []
        for location in self.properties()['backup_locations']:
            locations.append(BackupLocation.from_dict(location))
        return locations

    def latest_state_for(self, key):
        if self.state():
            if self.state()[key]:
                all_states = self.state()[key]
                latest_version = max(list(all_states.keys()))
                return FileState.from_dict(key, latest_version, self.state()[key][latest_version])
        return FileState(key, 'v0')

    def add_file_state(self, file_state):
        self.logger.debug('Updating state')

        if not file_state.key in self.state():
            self.state()[file_state.key] = {}

        self.state()[file_state.key][file_state.version] = {
            'size': file_state.size, 'date': file_state.date.isoformat()}
        self.write_state_to_file()

    def write_state_to_file(self):
        self.logger.debug('Writing state to disk...')
        f = open(self.file_location, 'w')
        json.dump(self.data, f, ensure_ascii=False, indent=4)
        f.close()
        self.logger.debug('State saved')
