from unittest import TestCase

from conf_publisher.page_maker import make_page, make_pages
from conf_publisher.confluence import Page
from conf_publisher.config import ConfigLoader


class FakeConfluencePageManager(object):

    def __init__(self, initial_pages=None):
        if initial_pages is None:
            initial_pages = []
        self._pages = dict((page.id, page) for page in initial_pages)

    def _get_last_content_id(self):
        if len(self._pages.keys()):
            return max(self._pages.keys())
        return 0

    def load(self, content_id):
        return self._pages[content_id]

    def create(self, page):
        content_id = self._get_last_content_id() + 1
        self._pages[content_id] = page
        return content_id

    def update(self, page, bump_version=True):
        if bump_version:
            page.version_number += 1
        self._pages[page.id] = page
        return page.id
    

def make_page_fixture(page_id=None, title=None, body=None, space_key='TEST'):
    p = Page()
    p.id = page_id
    p.space_key = space_key
    p.title = title
    p.body = body
    return p


class PageMakerTestCase(TestCase):

    def test_make_page(self):
        parent_page = make_page_fixture(page_id=40000000, title='parent page')
        page_manager = FakeConfluencePageManager([parent_page])
        page_id = make_page(parent_page, 'child page', page_manager)
        self.assertEqual(page_id, 40000001)

    def test_make_pages_with_parent_id(self):
        page_manager = FakeConfluencePageManager([
            make_page_fixture(page_id=40000000, title='parent page')
        ])

        config = ConfigLoader.from_dict({
            'version': 2,
            'base_dir': 'fixtures',
            'pages': [
                {
                    'title': 'child page',
                }
            ]
        })

        make_pages(config, page_manager, parent_id=40000000)
        self.assertTrue(40000001 in page_manager._pages)

    def test_make_pages_without_parent_id(self):
        page_manager = FakeConfluencePageManager([
            make_page_fixture(page_id=40000000, title='parent page')
        ])

        config = ConfigLoader.from_dict({
            'version': 2,
            'base_dir': 'fixtures',
            'pages': [
                {
                    'id': 40000000,
                    'title': 'parent page',
                    'pages': [
                        {
                            'title': 'child page',
                        }
                    ]
                }
            ]
        })

        make_pages(config, page_manager, parent_id=40000000)
        self.assertTrue(40000001 in page_manager._pages)
