import os
import json
import yaml

from .constants import DEFAULT_WATERMARK_CONTENT
from .errors import ConfigError


class Config(object):
    """
    This class provides storage, validation and conversion `config object` data.
    """

    def __getattr__(self, key):
        return self._config.get(key)

    def __setattr__(self, key, value):
        self._config[key] = value

    def __init__(self, config_path):
        self.__dict__['config_path'] = config_path
        with open(config_path, 'rb') as config:
            self.__dict__['_config'] = yaml.load(config)

        # Check config version
        if 'version' not in self._config:
            raise ConfigError('`version` param is required')

        if self._config['version'] != 2:
            raise ConfigError('invalid config version. required: 2')

        if 'pages' not in self._config:
            raise ConfigError('`pages` param is required')

    def get_config(self):
        return yaml.dump(self._config, default_flow_style=False)

    def update_config(self):
        with open(self.config_path, 'w') as f_config:
            f_config.write(self.get_config())

    @property
    def pages_iter(self):
        provider = DataProvider(self._config,  os.path.dirname(self.config_path))
        for page in self._config['pages']:
            yield Page(page, provider)


class Page(object):
    """
    This class provides storage, validation and conversion `page object` data.
    """

    watermark_template = '<p style="text-align: right;">' \
                         '<span style="color: rgb(153,153,153);">{watermark_content}</span>' \
                         '</p>'
    link_template = '<p style="text-align: right;">' \
                    '<a href="{link}" _blank="true">{link}</a>' \
                    '</p>'

    def __init__(self, page, provider):
        self._id = page.get('id')
        self._link = page.get('link')
        self._pages = page.get('pages', list())
        self._watermark_content = page.get('watermark', DEFAULT_WATERMARK_CONTENT)

        self._provider = provider

        source_filename, self._attachments = self._parse_page(page)
        self._title, self._body = provider.get_source_data(source_filename)

    def _parse_page(self, page):
        if 'source' not in page:
            raise KeyError('source not found')

        source_filename = self._provider.get_source(page['source'])

        atachments = page.get('attachments', dict())
        images = atachments.get('images', list())
        downloads = atachments.get('downloads', list())

        images_filenames = [self._provider.get_image(image) for image in images]
        downloads_filenames = [self._provider.get_attachment(download) for download in downloads]

        attachment_filenames = images_filenames + downloads_filenames

        return source_filename, attachment_filenames

    def inject_watermark(self):
        watermark = self.watermark_template.format(watermark_content=self._watermark_content)
        if self._link is not None:
            watermark += self.link_template.format(link=self._link)

        self._body = watermark + self._body

    def pages_iter(self):
        for page in self._pages:
            yield Page(page, self._provider)

    @property
    def attachments(self):
        return self._attachments

    @property
    def title(self):
        return self._title

    @property
    def body(self):
        return self._body

    @property
    def id(self):
        if self._id is None:
            raise AttributeError('Page id not in the configuration file. If pages not created, '
                                 'you may make this with "conf_page_maker" command')
        return self._id

    @property
    def pages(self):
        return self.pages_iter()


class DataProvider(object):
    def __init__(self, config, root='./'):
        if config is None:
            config = dict()

        self._root_dir = os.path.abspath(root)

        self._source_dir = config.get('base_dir', 'docs/build/json')
        if not os.path.isabs(self._source_dir):
            self._source_dir = os.path.join(self._root_dir, self._source_dir)

        self._downloads_dir = config.get('downloads_dir', '_downloads')
        if not os.path.isabs(self._downloads_dir):
            self._downloads_dir = os.path.join(self._source_dir, self._downloads_dir)

        self._images_dir = config.get('images_dir', '_images')
        if not os.path.isabs(self._images_dir):
            self._images_dir = os.path.join(self._source_dir, self._images_dir)

        self._source_ext = config.get('source_ext', '.fjson')

    def get_source(self, filename):
        return os.path.join(self._source_dir, filename + self._source_ext)

    @staticmethod
    def get_source_data(filename):
        with open(filename, 'r') as f:
            content = json.load(f)

        return content['title'], content['body']

    def get_image(self, filename):
        return os.path.join(self._images_dir, filename)

    def get_image_stream(self, filename):
        # TODO:
        pass

    def get_attachment(self, filename):
        return os.path.join(self._downloads_dir, filename)

    def get_attachment_stream(self, filename):
        # TODO:
        pass
