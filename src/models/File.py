import os


class File:
    """A file or folder that should be considered for backup"""

    def __init__(self, key, size, name, is_dir, parent_dir):
        self.key = key
        self.size = size
        self.name = name
        self.is_dir = is_dir
        self.parent_dir = parent_dir

    def get_path(self):
        return os.path.join(self.parent_dir, self.name)
