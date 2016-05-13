import os
import copy
from operator import attrgetter

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


class Content(object):
    type = None

    def __init__(self):
        self.id = None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


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
        self.ancestors = list()
        self.body = None
        self.title = None
        self.unused_title = None
        super(Page, self).__init__()

    def __eq__(self, other):
        first = copy.copy(self.__dict__)
        second = copy.copy(other.__dict__)

        del first['ancestors']
        del second['ancestors']
        if len(self.ancestors) != len(other.ancestors):
            return False

        for first_ancestor, second_ancestor in zip(self.ancestors, other.ancestors):
            if not (first_ancestor == second_ancestor):
                return False

        del first['body']
        del second['body']
        if not PageBodyComparator.is_equal(self.body, other.body):
            return False

        return first == second


class Ancestor(Content):
    type = 'page'


class ConfluenceManager(object):
    def __init__(self, api):
        self._api = api


class ConfluencePageManager(ConfluenceManager):

    def load(self, content_id):
        data = self._api.get_content(content_id, 'ancestors,version,space,body.storage')
        p = Page()
        p.id = data['id']
        p.type = data['type']
        p.version_number = data['version']['number']
        p.space_key = data['space']['key']
        p.title = data['title']
        p.body = data['body']['storage']['value']

        for ancestor_data in data['ancestors']:
            ancestor = Ancestor()
            ancestor.id = ancestor_data['id']
            ancestor.type = ancestor_data['type']
            p.ancestors.append(ancestor)

        return p

    def create(self, page):
        ancestor = page.ancestors[-1]

        data = self._page_payload(page.space_key, page.body, page.title,
                                  ancestor_id=ancestor.id, ancestor_type=ancestor.type,)
        ret = self._api.create_content(data)
        page.id = ret['id']
        return page.id

    def update(self, page, bump_version=True):
        if bump_version:
            page.version_number += 1

        ancestor = page.ancestors[-1]

        data = self._page_payload(page.space_key, page.body, page.title,
                                  ancestor_id=ancestor.id, ancestor_type=ancestor.type,
                                  content_id=page.id, version=page.version_number)
        ret = self._api.update_content(page.id, data)
        page.id = ret['id']
        return page.id

    @staticmethod
    def _page_payload(space_key, body=None, title=None,
                      ancestor_id=None, ancestor_type='page',
                      content_id=None, version=None, content_type='page'):
        payload = {
            'type': content_type,
            'space': {
                'key': space_key
            },
        }

        if body:
            payload['body'] = {
                'storage': {
                    'value': body,
                    'representation': 'storage'
                }
            }

        if ancestor_id:
            payload['ancestors'] = [
                {
                    'type': ancestor_type,
                    'id': ancestor_id,
                }
            ]

        if content_id:
            payload['id'] = content_id

        if title:
            payload['title'] = title

        if version:
            payload['version'] = {
                'number': version
            }

        return payload


class AttachmentPublisher(ConfluenceManager):
    def publish(self, content_id, filepath):
        attachments = self._get_page_metadata(content_id)
        filename = os.path.basename(filepath)

        if filename in map(attrgetter('title'), attachments):
            # TODO: fixme. skipping if file already exists. its ugly hack
            return

        with open(filepath, 'rb') as f:
            self._api.create_attachment(content_id, f)

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


class PageBodyComparator(object):

    @classmethod
    def is_equal(cls, first, second):
        if first == '' and second == '':
            return True

        if first == '' and second != '' or first != '' and second == '':
            return False

        # 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        # 'xsi:schemaLocation="http://www.atlassian.com/schema/confluence/4/ac/ confluence.xsd" '
        wrapper = u'<?xml version="1.0" encoding="UTF-8"?>' \
                  u'<!DOCTYPE ac:confluence SYSTEM "confluence.dtd">' \
                  u'<ac:confluence xmlns:ac="http://www.atlassian.com/schema/confluence/4/ac/" ' \
                  u'xmlns:ri="http://www.atlassian.com/schema/confluence/4/ri/">{}</ac:confluence>'

        first_xml = etree.XML(wrapper.format(first).encode(encoding='utf-8'), parser=cls._parser())
        second_xml = etree.XML(wrapper.format(second).encode(encoding='utf-8'), parser=cls._parser())
        return cls._elements_equal(first_xml, second_xml)

    @staticmethod
    def _parser():
        # use lxml HTMLParser if it exists
        if hasattr(etree, 'HTMLParser'):
            return etree.HTMLParser()

        # or xml.etree.ElementTree.XMLParser
        # fix unknown entity
        # http://stackoverflow.com/questions/7237466/python-elementtree-support-for-parsing-unknown-xml-entities
        parser = etree.XMLParser()
        parser.entity['nbsp'] = 'nbsp'
        return parser

    @classmethod
    def _elements_equal(cls, e1, e2):
        if e1.tag != e2.tag:
            return False
        if e1.text != e2.text:
            return False
        if not cls._attributes_equals(e1, e2):
            return False
        if len(e1) != len(e2):
            return False
        return all(cls._elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

    @staticmethod
    def _attributes_equals(e1, e2):
        # confluence create additional attributes for structured macros
        if 'structured-macro' == e1.tag:
            return e1.attrib.get('name') == e2.attrib.get('name')
        elif 'structured-macro' in e1.tag:
            confluence_ac_attribute_name = '{http://www.atlassian.com/schema/confluence/4/ac/}name'
            return e1.attrib.get(confluence_ac_attribute_name) == e2.attrib.get(confluence_ac_attribute_name)

        return e1.attrib == e2.attrib
