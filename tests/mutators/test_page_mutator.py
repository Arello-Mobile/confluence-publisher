from unittest import TestCase
from conf_publisher.mutators.page_mutator import WatermarkPageMutator
from conf_publisher.confluence import Page


class ConfigLoaderTestCase(TestCase):

    def test_watermark_page_mutator_add(self):
        watermark = 'test'
        content = 'page content'

        page = Page()
        page.body = content

        WatermarkPageMutator(watermark).add(page)

        self.assertNotEqual(content, page.body)

    def test_watermark_page_mutator_remove(self):
        watermark = 'test'
        clean_content = 'page content'

        page = Page()
        page.body = WatermarkPageMutator.template_prefix + \
                    WatermarkPageMutator.template.format(watermark=watermark) + \
                    WatermarkPageMutator.template_suffix + clean_content

        WatermarkPageMutator(watermark).remove(page)

        self.assertEqual(clean_content, page.body)
