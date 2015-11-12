import lxml.html
from . import log


class HtmlComparator(object):

    def __init__(self, old, new):
        self._old = old
        self._new = new

    def _remove_tag(self, html, tag):
        """
        Remove all tags from lxml.html.Element

        :param html: lxml.html.Element
        :param tag: str
        """
        elements = html.findall(tag)
        for tag in elements:
            html.remove(tag)

    def _remove_first_tag(self, html, tag):
        """
        Remove first tag from lxml.html.Element

        :param html: lxml.html.Element
        :param tag: str
        """
        el = html.find(tag)
        if el is not None:
            html.remove(el)

    def _diff(self, new, old):
        """
        :param new: lxml.html.Element
        :param old: lxml.html.Element
        :return: diff: bool
        """

        diff = False
        for sibling_new, sibling_old in zip(new, old):
            # Equal tags
            if sibling_new.tag != sibling_old.tag:
                diff = True
                break

            # Equal length
            if sibling_new.text != sibling_old.text:
                diff = True
                break

            children_new = sibling_new.getchildren()
            children_old = sibling_old.getchildren()

            # Children length
            if len(children_new) != len(children_old):
                diff = True
                break

            # Children not equal
            if self._diff(children_new, children_old):
                diff = True
                break

        return diff

    def compare(self):
        """
        :return: comapre: bool
        """
        if self._old == '' or self._new == '':
            return False

        old = lxml.html.fromstring(self._old)
        new = lxml.html.fromstring(self._new)

        self._remove_tag(new, 'structured-macro')
        self._remove_tag(old, 'structured-macro')

        diff = self._diff(new, old)
        log.info('Diff: %s' % diff)

        return diff
