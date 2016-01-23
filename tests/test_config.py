from unittest import TestCase
from conf_publisher.config import ConfigLoader, Config, PageConfig, flatten_page_config_list


class ConfigLoaderTestCase(TestCase):

    def test_config_loader_from_dict(self):
        data = {
            'version': 2,
            'url': 'https://confluence.com',
            'base_dir': 'result',
            'pages':
                [
                    {
                        'id': 52136662,
                        'source': 'release_history',
                    },
                ],
        }

        expected_page = PageConfig()
        expected_page.id = 52136662
        expected_page.source = 'release_history'

        expected = Config()
        expected.url = 'https://confluence.com'
        expected.base_dir = 'result'
        expected.pages.append(expected_page)

        result = ConfigLoader.from_dict(data)

        self.assertEqual(result, expected)


class UtilsTestCase(TestCase):

    def test_flatten_page_config_list(self):
        subsub_page = PageConfig()

        sub_page = PageConfig()
        sub_page.pages.append(subsub_page)

        page = PageConfig()
        page.pages.append(sub_page)

        config = Config()
        config.pages.append(page)

        pages = list(flatten_page_config_list(config.pages))
        self.assertEqual(len(list(pages)), 3)
