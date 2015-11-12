# coding: utf-8
import argparse

from . import log
from .confluence_api import create_confluence_api
from .publishers import PagePublisher, AttachmentPublisher
from .config import Config
from .confluence_pages import PageManager
from .constants import DEFAULT_CONFLUENCE_API_VERSION


class Publisher(object):
    def __init__(self, config, page_publisher, attachment_publisher):

        self._config = config
        self._page_publisher = page_publisher
        self._attachment_publisher = attachment_publisher

    def publish(self, page_manager, force=False, disable_watermark=False):
        # Load Pages
        pages = self._load_pages(self._config.pages_iter)

        # Inject watermark
        if not disable_watermark:
            self._inject_watermark(pages)

        # Filter page for change
        if not force:
            def filter_changed(page):
                return page_manager.check_diff(page.id, page.body)
            pages = filter(filter_changed, pages)

        #  Publish pages
        self._publish_pages(pages)

    def _load_pages(self, pages):
        pages_list = list()
        for page in pages:
            pages_list.append(page)
            pages_list += self._load_pages(page.pages)

        return pages_list

    @staticmethod
    def _inject_watermark(pages):
        for page in pages:
            page.inject_watermark()

    def _publish_pages(self, pages):
        for page in pages:
            self._publish_page(page)

    def _prepare_to_publish(self, page, disable_watermark):
        """
        Prepare page body. Check old and new page diff.
        """

        page.set_body(disable_watermark)
        diff = self._page_publisher.check_diff(page.id, page.body)
        return diff, page

    def _publish_page(self, page):
        log.info('Publishing page: id: %s' % page.id)

        content_id = self._page_publisher.publish(page.title, page.body, page.id)

        log.info('Published to: %s' % content_id)

        self._publish_page_attachments(content_id, page.attachments)

    def _publish_page_attachments(self, content_id, attachments):
        for attachment in attachments:
            self._publish_page_attachement(content_id, attachment)

    def _publish_page_attachement(self, content_id, filename):
        log.info('Publishing attachment: %s (parent_id: %s)' % (filename, content_id))

        self._attachment_publisher.publish(content_id, filename)

        log.info('Published to: %s' % content_id)


def main():
    """
    Parse Arguments
    """
    parser = argparse.ArgumentParser(description='Publish docs to Confluence')
    parser.add_argument('config', type=str, help='Configuration file')
    parser.add_argument('-u', '--url', type=str, help='Confluence Url')
    parser.add_argument('-a', '--auth', type=str, help='Base64 encoded user:password string')
    parser.add_argument('-F', '--force', action='store_true', help='Publish not changed page.')
    parser.add_argument('-dw', '--disable-watermark', action='store_true', help='Disable watermark flag')

    # TODO: add vvverbosity

    args = parser.parse_args()

    # Config
    config = Config(args.config)

    # Confluence API
    confluence_api = create_confluence_api(DEFAULT_CONFLUENCE_API_VERSION, config.url, args.auth)

    # Publishers
    page_publisher = PagePublisher(confluence_api)
    attachment_publisher = AttachmentPublisher(confluence_api)

    # Publish
    publisher = Publisher(config, page_publisher, attachment_publisher)

    page_manager = PageManager(confluence_api)
    publisher.publish(page_manager, args.force, args.disable_watermark)


if __name__ == '__main__':
    main()
