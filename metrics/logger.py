# Logger for cycle-level metrics

import json
import os

class Logger:
    def __init__(self, filename):
        self.filename = filename
        self.logs = []

    def log(self, entry):
        self.logs.append(entry)

    def save(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'w') as f:
            json.dump(self.logs, f, indent=2)
