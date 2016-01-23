import os

from . import DataProvider
from ..serializers import json_serializer


class SphinxFJsonDataProvider(DataProvider):
    def __init__(self, root_dir=None, base_dir=None, downloads_dir=None, images_dir=None, source_ext=None):
        self._root_dir = os.path.abspath(root_dir or './')

        self._source_dir = base_dir or 'docs/build/json'
        if not os.path.isabs(self._source_dir):
            self._source_dir = os.path.join(self._root_dir, self._source_dir)

        self._downloads_dir = downloads_dir or '_downloads'
        if not os.path.isabs(self._downloads_dir):
            self._downloads_dir = os.path.join(self._source_dir, self._downloads_dir)

        self._images_dir = images_dir or '_images'
        if not os.path.isabs(self._images_dir):
            self._images_dir = os.path.join(self._source_dir, self._images_dir)

        self._source_ext = source_ext or '.fjson'

    def get_source(self, filename):
        return os.path.join(self._source_dir, filename + self._source_ext)

    def get_source_data(self, filename):
        with open(filename, 'r') as f:
            content = json_serializer.load(f)

        return content['title'], content['body']

    def get_image(self, filename):
        return os.path.join(self._images_dir, filename)

    def get_attachment(self, filename):
        return os.path.join(self._downloads_dir, filename)
