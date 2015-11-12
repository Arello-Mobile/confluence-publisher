import argparse

from . import log
from .confluence_api import create_confluence_api
from .constants import DEFAULT_CONFLUENCE_API_VERSION
from .config import Config
from .publishers import PagePublisher


class PageMaker(object):

    def __init__(self, config, publisher, parent_id):
        self._config = config
        self._publisher = publisher
        self._parent_id = parent_id

    def make_pages(self):
        self._make_pages(self._config.pages_iter, self._config.pages, self._parent_id)

        self._config.update_config()
        log.info('Config has been updated.')

    def _make_pages(self, iterator, obj, parent_id):
        for i, page in enumerate(iterator):
            if page._id is None:
                page_id = self._publisher.create_blank_page(parent_id, page.title)
                log.info('Page with id %s has been created. Parent page id: %d' % (page_id, parent_id))
                obj[i]['id'] = int(page_id)
            else:
                page_id = page.id

            self._make_pages(page.pages, obj[i].get('pages', list()), int(page_id))


def main():
    parser = argparse.ArgumentParser(description='Make confluence page and write this ids to config')
    parser.add_argument('config', type=str, help='Configuration file')
    parser.add_argument('-a', '--auth', type=str, help='Base64 encoded user:password string')
    parser.add_argument('-pid', '--parent-id', type=str, help='Parent page ID in confluence.')

    args = parser.parse_args()

    config = Config(args.config)
    confluence_api = create_confluence_api(DEFAULT_CONFLUENCE_API_VERSION, config.url, args.auth)

    publisher = PagePublisher(confluence_api)

    maker = PageMaker(config, publisher, args.parent_id)
    maker.make_pages()


if __name__ == '__main__':
    main()
