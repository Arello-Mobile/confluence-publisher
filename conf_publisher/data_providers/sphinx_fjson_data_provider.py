import os
from .sphinx_base_data_provider import SphinxBaseDataProvider
from ..serializers import json_serializer


class SphinxFJsonDataProvider(SphinxBaseDataProvider):
    DEFAULT_SOURCE_EXT = '.fjson'
    DEFAULT_SOURCE_DIR = 'docs/build/json'

    def get_source_data(self, filename):
        if os.path.isabs(filename):
            filepath = filename
        else:
            filepath = self.get_source(filename)
        with open(filepath, 'r') as f:
            content = json_serializer.load(f)

        return content.get('title'), content.get('body')
