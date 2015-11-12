from .html_comaprator import HtmlComparator


class PageManager(object):

    def __init__(self, api):
        self._api = api

    def check_diff(self, page_id, body):
        old_page_content = self._api.get_content(page_id, expand='body.storage')
        comparator = HtmlComparator(old_page_content['body']['storage']['value'], body)
        return comparator.compare()
