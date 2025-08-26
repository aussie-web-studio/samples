import os
import json
from agentcore_app.config import Config

class ResourceStore:
    def __init__(self, filename=None):
        self.filename = filename or Config.RESOURCE_STORE_FILE

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return {}

    def save(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2)
