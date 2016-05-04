from .sphinx_base_data_provider import SphinxBaseDataProvider
import re
import codecs


class SphinxHTMLDataProvider(SphinxBaseDataProvider):
    DEFAULT_SOURCE_EXT = '.html'
    DEFAULT_SOURCE_DIR = 'docs/build/html'

    def get_source_data(self, filename):
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            title = re.findall(r'<title.*?>(.+?)</title>', content)[0]
            body = re.findall(r'<body.*?>(.+?)</body>', content, re.DOTALL)[0].strip()

        return title, body
