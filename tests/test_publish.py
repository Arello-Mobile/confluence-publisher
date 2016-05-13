from unittest import TestCase
import random
import os

from conf_publisher.confluence import Page
from conf_publisher.publish import Publisher
from conf_publisher.config import ConfigLoader
from conf_publisher.data_providers.sphinx_fjson_data_provider import SphinxFJsonDataProvider


class FakePagePublisher(object):
    def __init__(self, pages=None):
        pages = pages or []
        self._pages = dict((page.id, page) for page in pages)

    def load(self, content_id):
        return self._pages[content_id]

    def create(self, page):
        page.id = random.randint(10000, 100000)
        self._pages[page.id] = page
        return page.id

    def update(self, page, bump_version=True):
        self._pages[page.id] = page
        return page.id


class FakeAttachmentPublisher(object):
    def publish(self, content_id, filename):
        return random.randint(10000, 100000)


class PublisherTestCase(TestCase):

    def test_attachment_publish(self):
        config = ConfigLoader.from_dict({
            'version': 2,
            'base_dir': 'fixtures',
            'pages': [
                {
                    'id': 1,
                    'source': 'page',
                    'attachments': {
                        'images': [
                            'test_image.png'
                        ],
                        'downloads': [
                            'test_download.txt'
                        ],
                    }
                },
                {
                    'id': 1,
                    'source': 'page',
                    'title': 'cfgTitle'
                },
                {
                    'id': 1,
                    'source': 'titeless_page',
                    'watermark': 'just mark it!',
                    'link': 'http://localhost:8080/index.htm'
                }
            ]
        })

        page = Page()
        page.id = 1
        page.title = u'pageTitle'
        page.unused_title = u'Useless'
        page.body = u'''
            Body
            <a href="{}">Title</a>
            <a href="{}">Unused</a>
        '''.format(page.title, page.unused_title)

        tests_root = os.path.dirname(os.path.abspath(__file__))
        data_provider = SphinxFJsonDataProvider(root_dir=tests_root, base_dir=config.base_dir)
        page_manager = FakePagePublisher([page])
        attachment_manager = FakeAttachmentPublisher()

        publisher = Publisher(config, data_provider, page_manager, attachment_manager)
        publisher.publish()

        publisher = Publisher(config, data_provider, page_manager, attachment_manager)
        publisher.publish(force=True, watermark=True, hold_titles=True)

        publisher = Publisher(config, data_provider, page_manager, attachment_manager)
        publisher.publish(force=True, watermark=True, hold_titles=False)

        publisher = Publisher(config, data_provider, page_manager, attachment_manager)
        publisher.publish(force=True, watermark=False, hold_titles=False)

        publisher = Publisher(config, data_provider, page_manager, attachment_manager)
        publisher.publish(force=False, watermark=False, hold_titles=True)

        publisher = Publisher(config, data_provider, page_manager, attachment_manager)
        publisher.publish(force=False, watermark=True, hold_titles=False)
