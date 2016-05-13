import argparse
import copy

from . import log, setup_logger
from .confluence_api import create_confluence_api
from .confluence import ConfluencePageManager, AttachmentPublisher
from .config import ConfigLoader, flatten_page_config_list, PageImageAattachmentConfig
from .constants import DEFAULT_CONFLUENCE_API_VERSION, DEFAULT_WATERMARK_CONTENT
from .data_providers.sphinx_fjson_data_provider import SphinxFJsonDataProvider
from .data_providers.sphinx_html_data_provider import SphinxHTMLDataProvider
from .mutators.page_mutator import WatermarkPageMutator, LinkPageMutator, AnchorPageMutator


def get_data_provider_class(config):
    if config.source_ext == '.html':
        data_provider_class = SphinxHTMLDataProvider
    else:
        data_provider_class = SphinxFJsonDataProvider
    return data_provider_class


def create_publisher(config, confluence_api):
    page_manager = ConfluencePageManager(confluence_api)
    attachment_publisher = AttachmentPublisher(confluence_api)

    data_provider_class = get_data_provider_class(config)

    data_provider = data_provider_class(
        base_dir=config.base_dir,
        downloads_dir=config.downloads_dir,
        images_dir=config.images_dir,
        source_ext=config.source_ext
    )
    return Publisher(config, data_provider, page_manager, attachment_publisher)


class Publisher(object):
    def __init__(self, config, data_provider, page_manager, attachment_manager):
        self._config = config
        self._data_provider = data_provider
        self._page_manager = page_manager
        self._attachment_manager = attachment_manager

    @staticmethod
    def _page_title(current_title, new_title, config_title=None, hold_current=False):
        result = None
        if hold_current:
            result = current_title
        elif config_title:
            result = config_title
        elif new_title:
            result = new_title
        else:
            result = current_title
        return result

    def _page(self, current_page, source):
        page = copy.copy(current_page)
        page.title, page.body = self._data_provider.get_source_data(self._data_provider.get_source(source))
        return page

    def _page_attachment_file(self, attachment_config):
        if isinstance(attachment_config, PageImageAattachmentConfig):
            return self._data_provider.get_image(attachment_config.path)
        return self._data_provider.get_attachment(attachment_config.path)

    @staticmethod
    def _remove_page_mutators(page, mutators):
        for mutator in mutators:
            mutator.apply_backward(page)

    @staticmethod
    def _add_page_mutators(page, mutators):
        for mutator in mutators:
            mutator.apply_forward(page)

    def _init_page_mutators(self, page_config, old_title, hold_titles):
        mutators = []

        if page_config.link:
            mutators.append(LinkPageMutator(page_config.link))
        if page_config.watermark:
            mutators.append(WatermarkPageMutator(page_config.watermark))
        if hold_titles:
            mutators.append(AnchorPageMutator(old_title))

        return mutators

    def _pages_to_update(self, force=False, watermark=False, hold_titles=False):
        pages_to_update = []
        for page_config in flatten_page_config_list(self._config.pages):
            if page_config.id is None:
                raise AttributeError('Missed attribute "id"')
            current_page = self._page_manager.load(page_config.id)
            page = self._page(current_page, page_config.source)

            mutators = self._init_page_mutators(page_config, page.title, hold_titles)
            self._remove_page_mutators(current_page, mutators)

            page.title = self._page_title(current_page.title, page.title, page_config.title, hold_titles)
            if not force and current_page == page:
                continue

            self._add_page_mutators(page, mutators)

            pages_to_update.append(page)
        return pages_to_update

    def _attachments_to_update(self, force=False):
        attachments_to_update = []
        for page_config in flatten_page_config_list(self._config.pages):
            for attachment_config in page_config.images + page_config.downloads:
                page_attachment = (page_config.id, self._page_attachment_file(attachment_config))
                attachments_to_update.append(page_attachment)
        return attachments_to_update

    def publish(self, force=False, watermark=False, hold_titles=False):
        pages_to_update = self._pages_to_update(force, watermark, hold_titles)
        attachments_to_update = self._attachments_to_update(force)

        log.info('Publishing pages...')
        self._publish_pages(pages_to_update)

        log.info('Publishing attachments...')
        self._publish_attachments(attachments_to_update)

    def _publish_pages(self, pages):
        for page in pages:
            self._publish_page(page)

    def _publish_page(self, page):
        log.info('Publishing page: id: %s' % page.id)
        content_id = self._page_manager.update(page)
        log.info('Published to: %s' % content_id)

    def _publish_attachments(self, attachments):
        for content_id, attachment in attachments:
            self._publish_page_attachement(content_id, attachment)

    def _publish_page_attachement(self, content_id, filename):
        log.info('Publishing attachment: %s (parent_id: %s)' % (filename, content_id))
        self._attachment_manager.publish(content_id, filename)
        log.info('Published to: %s' % content_id)


def setup_config_overrides(config, url=None, watermark=None, link=None):
    if url:
        config.url = url

    if watermark:
        for page in flatten_page_config_list(config.pages):
            if watermark.lower() == 'false':
                page.watermark = None
            elif watermark.lower() == 'true':
                page.watermark = DEFAULT_WATERMARK_CONTENT
            else:
                page.watermark = watermark

    if link:
        for page in flatten_page_config_list(config.pages):
            if link.lower() == 'false':
                page.link = None
            else:
                page.link = link


def main():
    parser = argparse.ArgumentParser(description='Publish documentation (Sphinx fjson) to Confluence')
    parser.add_argument('config', type=str, help='Configuration file')
    parser.add_argument('-u', '--url', type=str, help='Confluence Url')
    parser.add_argument('-a', '--auth', type=str, help='Base64 encoded user:password string')
    parser.add_argument('-F', '--force', action='store_true', help='Publish not changed page.')
    parser.add_argument('-w', '--watermark', type=str, help='Overrides the watermarks. Also can be "False" to remove '
                                                            'all watermarks; or "True" to add watermarks'
                                                            'with default text: "{}" on all pages.'.format(DEFAULT_WATERMARK_CONTENT))
    parser.add_argument('-l', '--link', type=str, help='Overrides page link. If value is "False" then removes the link.')
    parser.add_argument('-ht', '--hold-titles', action='store_true', help='Do not change page titles while publishing.')
    parser.add_argument('-v', '--verbose', action='count')

    args = parser.parse_args()

    setup_logger(args.verbose)

    config = ConfigLoader.from_yaml(args.config)

    setup_config_overrides(config, args.url, args.watermark, args.link)

    confluence_api = create_confluence_api(DEFAULT_CONFLUENCE_API_VERSION, config.url, args.auth)
    publisher = create_publisher(config, confluence_api)
    publisher.publish(args.force, args.watermark, args.hold_titles)

if __name__ == '__main__':
    main()
