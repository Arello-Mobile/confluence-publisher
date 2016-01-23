from unittest import TestCase
import copy
import os
import codecs

from conf_publisher.confluence import Page, Content, Ancestor, PageBodyComparator


class ContentTestCase(TestCase):

    def test_eq(self):
        first = Content()
        first.id = 123
        first.type = 'page'

        second = copy.deepcopy(first)

        self.assertTrue(first == second)


class PageTestCase(TestCase):

    def test_eq(self):
        fixture_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'page_body.html')
        body_fixture = codecs.open(fixture_file, 'r', encoding='utf-8').read()

        first_ancestor = Ancestor()
        first_ancestor.id = 12344

        first = Page()
        first.id = 12345
        first.type = 'page'
        first.body = body_fixture

        first.ancestors.append(first_ancestor)

        second = copy.deepcopy(first)

        self.assertTrue(first == second)


class PageBodyComparatorTestCase(TestCase):

    def test_is_equal(self):
        fixture_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'page_body.html')
        body_fixture = codecs.open(fixture_file, 'r', encoding='utf-8').read()

        fixture_file_stripped = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'page_body_stripped.html')
        body_fixture_stripped = codecs.open(fixture_file_stripped, 'r', encoding='utf-8').read()

        result = PageBodyComparator.is_equal(body_fixture, body_fixture_stripped)
        self.assertTrue(result)

    def test_attributes(self):
        first = """<ac:structured-macro ac:name="code"></ac:structured-macro>"""
        second = """<ac:structured-macro ac:name="code" ac:macro-id="3a4340a5-f3e7-4a93-9d8a-8017715fbc94"></ac:structured-macro>"""

        result = PageBodyComparator.is_equal(first, second)
        self.assertTrue(result)
