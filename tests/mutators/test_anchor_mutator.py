from unittest import TestCase
from conf_publisher.mutators.page_mutator import AnchorPageMutator
from conf_publisher.confluence import Page


class ConfigLoaderTestCase(TestCase):

    # TODO change regular expression to match only anchor
    def test_anchor_page_mutator_mutate(self):
        original_content = u'''
            <p>Default response</p>\n<p>Type: <a class="reference internal" href="#SnowTeq1.0.0-d-c40da07e339eaa512fd6189

            f="#SnowTeq1.0.0-d-c40da07e339eaa512fd6189758a42db6"><span>ClubsSerializer</span></a></p>\n<p><strong>Example
            <a class="reference internal" href="#SnowTeq1.0.0-d-c40da07e339eaa512fd6189758a42db6"><span>ClubsSerializer</
        '''
        correct_content = u'''
            <p>Default response</p>\n<p>Type: <a class="reference internal" href="#TestPage#2-d-c40da07e339eaa512fd6189

            f="#TestPage#2-d-c40da07e339eaa512fd6189758a42db6"><span>ClubsSerializer</span></a></p>\n<p><strong>Example
            <a class="reference internal" href="#TestPage#2-d-c40da07e339eaa512fd6189758a42db6"><span>ClubsSerializer</
        '''
        page_new_title = u'SnowTeq 1.0.0'
        page_old_title = u'Test Page #2'

        page = Page()
        page.body = original_content
        # means hold-title = True
        page.title = page_old_title

        AnchorPageMutator(page_new_title).apply_forward(page)

        self.assertEqual(correct_content, page.body)
