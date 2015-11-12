import os
import random
from operator import attrgetter

from . import log


class Content(object):
    type = None

    def __init__(self):
        self.id = None


class Attachement(Content):
    type = 'attachment'

    def __init__(self):
        self.title = ''
        self.media_type = ''
        super(Attachement, self).__init__()


class ImageAttachement(Attachement):
    pass


class DownloadAttachement(Attachement):
    pass


class Page(Content):
    type = 'page'

    def __init__(self):
        self.version_number = 0
        self.space_key = None
        super(Page, self).__init__()


class Ancestor(Content):
    type = 'page'


class ConfluencePublisher(object):
    def __init__(self, api):
        self._api = api


class PagePublisher(ConfluencePublisher):
    def publish(self, title, body, content_id):
        return self._update_page(content_id, title, body)

    def create_blank_page(self, parent_id, title):
        return self._create_page(parent_id, title, '')

    @staticmethod
    def _parse_page(data):
        p = Page()
        p.id = data['id']
        p.type = data['type']
        p.version_number = data['version']['number']
        p.space_key = data['space']['key']
        return p

    @staticmethod
    def _parse_ancestors(data):
        ancestors = []
        for ancestor_data in data['ancestors']:
            ancestor = Ancestor()
            ancestor.id = ancestor_data['id']
            ancestor.type = ancestor_data['type']

            ancestors.append(ancestor)

        return ancestors

    def _get_page_metadata(self, content_id):
        data = self._api.get_content(content_id, 'ancestors,version,space')

        page = self._parse_page(data)
        ancestors = self._parse_ancestors(data)

        return page, ancestors

    def _update_page(self, content_id, title, body):
        page, ancestors = self._get_page_metadata(content_id)

        if len(ancestors) == 0:
            raise RuntimeError('page has no parent')

        space_key = page.space_key
        ancestor_id = ancestors[-1].id
        version = page.version_number + 1

        data = self._page_payload(space_key, ancestor_id, title, body, content_id=content_id, version=version)
        ret = self._api.update_content(content_id, data)

        content_id = ret['id']
        return content_id

    def _create_page(self, parent_id, title, body):
        parent_page, _ = self._get_page_metadata(parent_id)
        data = self._page_payload(parent_page.space_key, parent_id, title, body)
        ret = self._api.create_content(data)

        content_id = ret['id']
        return content_id

    @staticmethod
    def _page_payload(space_key, ancestor_id, title='', body='', content_id=None, ancestor_type='page', version=None, content_type='page'):
        payload = {
            'id': content_id,
            'type': content_type,
            'title': title,
            'space': {
                'key': space_key
            },
            'version': {
                'number': version
            },
            'body': {
                'storage': {
                    'value': body,
                    'representation': 'storage'
                }
            },
            'ancestors': [
                {
                    'type': ancestor_type,
                    'id': ancestor_id,
                }
            ]
        }

        # TODO: fixme
        if content_id is None:
            del payload['id']

        if version is None:
            del payload['version']

        return payload


class AttachmentPublisher(ConfluencePublisher):
    def publish(self, content_id, filepath):
        attachments = self._get_page_metadata(content_id)
        filename = os.path.basename(filepath)

        if filename in map(attrgetter('title'), attachments):
            # TODO: fixme. skipping if file already exists. its ugly hack
            return

        with open(filepath, 'rb') as f:
            self._api.create_attachment(content_id, f)

    def _publish(self, content_id, stream):
        log.info('Publishing attachment: %s to %s', stream.name, content_id)
        ret = self._api.create_attachment(content_id, stream)
        log.debug('ret = %s', ret)
        return ret

    @staticmethod
    def _parse_attachments(data):
        attachments = []
        for attachment_data in data['children']['attachment']['results']:
            media_type = attachment_data['metadata']['mediaType']
            attachment_class = ImageAttachement if 'image' in media_type else DownloadAttachement
            attachment = attachment_class()
            attachment.id = attachment_data['id']
            attachment.title = attachment_data['title']
            attachment.media_type = media_type

            attachments.append(attachment)

        return attachments

    def _get_page_metadata(self, content_id):
        data = self._api.get_content(content_id, 'children.attachment')

        page_attachments = self._parse_attachments(data)

        return page_attachments


class FakePagePublisher(ConfluencePublisher):
    def publish(self, title, body, content_id=None, parent_id=None):
        if content_id is not None:
            return content_id

        if parent_id is not None:
            return parent_id + random.randint(10000, 100000)

        raise ValueError('content_id is none')


class FakeAttachmentPublisher(ConfluencePublisher):
    def publish(self, content_id, filename):
        return random.randint(10000, 100000)
