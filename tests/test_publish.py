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

    def get(self):
        return self._pages.values()


class FakeAttachmentPublisher(object):
    def publish(self, content_id, filename):
        return random.randint(10000, 100000)


class FakeEnv(object):
    def __init__(self):
        self.config = ConfigLoader.from_dict({
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

        self.tests_root = os.path.dirname(os.path.abspath(__file__))
        self.data_provider = SphinxFJsonDataProvider(root_dir=self.tests_root, base_dir=self.config.base_dir)
        self.page_manager = FakePagePublisher([page])
        self.attachment_manager = FakeAttachmentPublisher()

    def items(self):
        return [self.config, self.data_provider, self.page_manager, self.attachment_manager]


class PublisherTestCase(TestCase):
    title1 = u'pageTitle'
    body1 = u'''<span class="WATERMARK BEGIN"> </span><ac:structured-macro ac:name="info">
        <ac:rich-text-body>
        <p><span>just mark it!</span></p>
        </ac:rich-text-body>
        </ac:structured-macro><span class="WATERMARK END"> </span><span class="LINK BEGIN"> </span><ac:structured-macro ac:name="info">
        <ac:rich-text-body>
        <p><span><a href="http://localhost:8080/index.htm" _blank="true">http://localhost:8080/index.htm</a></span></p>
        </ac:rich-text-body>
        </ac:structured-macro><span class="LINK END"> </span>Body'''

    def test_default_publish(self):
        env = FakeEnv()
        publisher = Publisher(*env.items())
        publisher.publish()
        _page = env.items()[2].get()
        #self.assertEqual(_page[0].title, self.title1)
        #self.assertEqual(_page[0].body, self.body1)

    def test_111_publish(self):
        env = FakeEnv()
        publisher = Publisher(*env.items())
        publisher.publish(force=True, watermark=True, hold_titles=True)
        _page = env.items()[2].get()
        #self.assertEqual(_page[0].title, self.title1)
        #self.assertEqual(_page[0].body, u'')

    def test_110_publish(self):
        env = FakeEnv()
        publisher = Publisher(*env.items())
        publisher.publish(force=True, watermark=True, hold_titles=False)
        _page = env.items()[2].get()
        #self.assertEqual(_page[0].title, self.title1)
        #self.assertEqual(_page[0].body, self.body1)

    def test_100_publish(self):
        env = FakeEnv()
        publisher = Publisher(*env.items())
        publisher.publish(force=True, watermark=False, hold_titles=False)
        _page = env.items()[2].get()
        #self.assertEqual(_page[0].title, self.title1)
        #self.assertEqual(_page[0].body, self.body1)

    def test_001_publish(self):
        env = FakeEnv()
        publisher = Publisher(*env.items())
        publisher.publish(force=False, watermark=False, hold_titles=True)
        _page = env.items()[2].get()
        #self.assertEqual(_page[0].title, self.title1)
        #self.assertEqual(_page[0].body, self.body1)

    def test_010_publish(self):
        env = FakeEnv()
        publisher = Publisher(*env.items())
        publisher.publish(force=False, watermark=True, hold_titles=False)
        _page = env.items()[2].get()
        #self.assertEqual(_page[0].title, self.title1)
        #self.assertEqual(_page[0].body, self.body1)

