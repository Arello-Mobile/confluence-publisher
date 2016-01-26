import copy
from collections import OrderedDict

from .errors import ConfigError
from .serializers import yaml_serializer


class Config(object):
    def __init__(self):
        self.url = None
        self.base_dir = None
        self.downloads_dir = None
        self.images_dir = None
        self.source_ext = None
        self.pages = list()

    def __eq__(self, other):
        first = copy.copy(self.__dict__)
        del first['pages']

        second = copy.copy(other.__dict__)
        del second['pages']

        if len(self.pages) != len(other.pages):
            return False

        for first_page, second_page in zip(self.pages, other.pages):
            if not (first_page == second_page):
                return False

        return first == second


class PageConfig(object):
    def __init__(self):
        self.id = None

        self.title = None
        self.source = None
        self.link = None
        self.watermark = None

        self.images = list()
        self.downloads = list()

        self.pages = list()

    def __eq__(self, other):
        first = copy.copy(self.__dict__)
        del first['images']
        del first['downloads']

        second = copy.copy(other.__dict__)
        del second['images']
        del second['downloads']

        if len(self.images) != len(other.images):
            return False

        if len(self.downloads) != len(other.downloads):
            return False

        for first_attach, second_attach in zip(self.images, other.images):
            if not (first_attach == second_attach):
                return False

        for first_attach, second_attach in zip(self.downloads, other.downloads):
            if not (first_attach == second_attach):
                return False

        return first == second


class PageAattachmentConfig(object):
    TYPE_ATTACHMENT = 'attachment'
    TYPE_IMAGE = 'image'

    def __init__(self):
        self.type = self.TYPE_ATTACHMENT
        self.path = None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class PageImageAattachmentConfig(PageAattachmentConfig):
    def __init__(self):
        self.type = self.TYPE_IMAGE
        super(PageImageAattachmentConfig, self).__init__()


class ConfigLoader:

    @classmethod
    def from_yaml(cls, config_path):
        with open(config_path, 'rb') as f:
            config = yaml_serializer.load(f)
        return cls.from_dict(config)

    @classmethod
    def from_dict(cls, config_dict):
        if 'version' not in config_dict:
            raise ConfigError('`version` param is required')

        if config_dict['version'] != 2:
            raise ConfigError('invalid config version. required: 2')

        config = Config()

        for attr in ('url', 'base_dir', 'downloads_dir', 'images_dir', 'source_ext'):
            if attr in config_dict:
                setattr(config, attr, config_dict[attr])

        config.pages = cls._pages_from_list(config_dict.get('pages', list()))

        return config

    @classmethod
    def _pages_from_list(cls, pages_list):
        pages = list()
        for page_dict in pages_list:
            pages.append(cls._page_from_dict(page_dict))
        return pages

    @classmethod
    def _page_from_dict(cls, page_dict):
        page_config = PageConfig()

        for attr in ('id', 'title', 'source', 'link', 'watermark'):
            if attr in page_dict:
                setattr(page_config, attr, page_dict[attr])

        if 'attachments' in page_dict:
            for path in page_dict['attachments'].get('images', list()):
                page_config.images.append(cls._attach_from_path(path, PageImageAattachmentConfig))
            for path in page_dict['attachments'].get('downloads', list()):
                page_config.downloads.append(cls._attach_from_path(path, PageAattachmentConfig))

        page_config.pages = cls._pages_from_list(page_dict.get('pages', list()))

        return page_config

    @staticmethod
    def _attach_from_path(attach_path, attach_class):
        attach = attach_class()
        attach.path = attach_path
        return attach


class ConfigDumper:
    @classmethod
    def to_yaml_file(cls, config, config_path):
        with open(config_path, 'w') as f:
            cls.to_yaml_string(config, stream=f)

    @classmethod
    def to_yaml_string(cls, config, stream=None):
        return yaml_serializer.dump(cls.to_dict(config), stream=stream)

    @classmethod
    def to_dict(cls, config):
        config_dict = OrderedDict(version=2)

        for attr in ('url', 'base_dir', 'downloads_dir', 'images_dir', 'source_ext'):
            attr_value = getattr(config, attr)
            if attr_value:
                config_dict[attr] = attr_value

        config_dict['pages'] = cls._pages_to_list(config.pages)

        return config_dict

    @classmethod
    def _pages_to_list(cls, pages_config):
        pages = list()
        for page_config in pages_config:
            pages.append(cls._page_to_dict(page_config))
        return pages

    @classmethod
    def _page_to_dict(cls, page_config):
        page_dict = OrderedDict()

        for attr in ('id', 'title', 'source', 'link', 'watermark'):
            attr_value = getattr(page_config, attr)
            if attr_value:
                page_dict[attr] = attr_value

        if len(page_config.images) + len(page_config.downloads):
            page_dict['attachments'] = OrderedDict()
        if len(page_config.images):
            page_dict['attachments']['images'] = cls._attaches_to_path(page_config.images)
        if len(page_config.images):
            page_dict['attachments']['downloads'] = cls._attaches_to_path(page_config.downloads)

        pages = cls._pages_to_list(page_config.pages)
        if len(pages):
            page_dict['pages'] = pages

        return page_dict

    @classmethod
    def _attaches_to_path(cls, attaches):
        attaches_list = []
        for attach_config in attaches:
            attaches_list.append(cls._attach_to_path(attach_config))
        return attaches_list

    @staticmethod
    def _attach_to_path(attach_config):
        return attach_config.path


def flatten_page_config_list(pages):
    for page in pages:
        yield page
        for subpage in flatten_page_config_list(page.pages):
            yield subpage
