import argparse

from . import log, setup_logger
from .auth import parse_authentication
from .confluence_api import create_confluence_api
from .constants import DEFAULT_CONFLUENCE_API_VERSION
from .config import ConfigLoader, ConfigDumper
from .confluence import ConfluencePageManager, Page, Ancestor


def setup_config_overrides(config, url=None):
    if url:
        config.url = url


def empty_page(space_key, title, ancestor_id, ancestor_type):
    ancestor = Ancestor()
    ancestor.id = ancestor_id
    ancestor.type = ancestor_type

    page = Page()
    page.space_key = space_key
    page.title = title
    page.body = ''
    page.ancestors.append(ancestor)

    return page


def make_page(parent_page, title, page_manager):
    page = empty_page(parent_page.space_key, title, parent_page.id, parent_page.type)
    page_id = page_manager.create(page)
    return int(page_id)


def make_pages(config, page_manager, parent_id=None):
    parent_page = None
    if parent_id:
        parent_page = page_manager.load(parent_id)

    for page_config in config.pages:
        if not page_config.id:
            if not parent_page:
                log.warning('Page without id and parent page. Skip.')
            elif not page_config.title:
                log.warning('Page without title. Skip. Parent page id: {parent_id}.'.format(parent_id=parent_id))
            else:
                page_config.id = make_page(parent_page, page_config.title, page_manager)
                log.info('Page with id {page_id} has been created. Parent page id: {parent_id}'
                         .format(page_id=page_config.id, parent_id=parent_page.id))
        else:
            log.info('Skip page with id {page_id}'.format(page_id=page_config.id))

        if len(page_config.pages):
            make_pages(page_config, page_manager, page_config.id)


def main():
    parser = argparse.ArgumentParser(description='Create Confluence pages and update configuration file with it ids')
    parser.add_argument('config', type=str, help='Configuration file')
    parser.add_argument('-u', '--url', type=str, help='Confluence Url')
    auth_group = parser.add_mutually_exclusive_group(required=True)
    auth_group.add_argument('-a', '--auth', type=str, help='Base64 encoded user:password string')
    auth_group.add_argument('-U', '--user', type=str, help='Username (prompt password)')
    parser.add_argument('-t', '--auth-type', choices=['basic', 'session'], help='Use "session" for servers with Basic HTTP disabled')
    parser.add_argument('-pid', '--parent-id', type=str, help='Parent page ID in confluence.')
    parser.add_argument('-v', '--verbose', action='count')

    args = parser.parse_args()
    auth = parse_authentication(args.auth, args.user, args.auth_type)
    setup_logger(args.verbose)

    config = ConfigLoader.from_yaml(args.config)
    setup_config_overrides(config, args.url)

    confluence_api = create_confluence_api(DEFAULT_CONFLUENCE_API_VERSION, config.url, auth)
    page_manager = ConfluencePageManager(confluence_api)
    make_pages(config, page_manager, args.parent_id)

    ConfigDumper.to_yaml_file(config, args.config)
    log.info('Config has been updated.')

if __name__ == '__main__':
    main()
