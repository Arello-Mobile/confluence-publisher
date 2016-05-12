import os

from . import DataProvider


class SphinxBaseDataProvider(DataProvider):

    DEFAULT_SOURCE_EXT = None
    DEFAULT_ROOT_DIR = './'
    DEFAULT_SOURCE_DIR = 'docs/build/result'
    DEFAULT_IMAGES_DIR = '_images'
    DEFAULT_DOWNLOADS_DIR = '_downloads'

    def __init__(self, root_dir=None, base_dir=None, downloads_dir=None, images_dir=None, source_ext=None):
        self._root_dir = os.path.abspath(root_dir or './')

        self._source_dir = base_dir or self.DEFAULT_SOURCE_DIR
        if not os.path.isabs(self._source_dir):
            self._source_dir = os.path.join(self._root_dir, self._source_dir)

        self._downloads_dir = downloads_dir or self.DEFAULT_DOWNLOADS_DIR
        if not os.path.isabs(self._downloads_dir):
            self._downloads_dir = os.path.join(self._source_dir, self._downloads_dir)

        self._images_dir = images_dir or self.DEFAULT_IMAGES_DIR
        if not os.path.isabs(self._images_dir):
            self._images_dir = os.path.join(self._source_dir, self._images_dir)

        self._source_ext = source_ext or self.DEFAULT_SOURCE_EXT

    def get_source(self, filename):
        return os.path.join(self._source_dir, filename + self._source_ext)

    def get_source_data(self, filename):
        raise NotImplementedError()

    def get_image(self, filename):
        return os.path.join(self._images_dir, filename)

    def get_attachment(self, filename):
        return os.path.join(self._downloads_dir, filename)
