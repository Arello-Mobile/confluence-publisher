import re


class PageMutator(object):

    def add(self, page):
        raise NotImplemented()

    def remove(self, page):
        raise NotImplemented()


class TemplatePageMutator(PageMutator):
    template_prefix = None
    template_suffix = None
    template = None

    def __init__(self):
        self.template_params = {}

    def set_param(self, name, value):
        self.template_params[name] = value

    def add(self, page):
        page.body = self.template_prefix + self.template.format(**self.template_params) + self.template_suffix + page.body

    def remove(self, page):
        page.body = re.sub(re.escape(self.template_prefix) + '.*' + re.escape(self.template_suffix), '', page.body, flags=re.DOTALL)


class WatermarkPageMutator(TemplatePageMutator):
    template_prefix = '<span class="WATERMARK BEGIN"> </span>'
    template_suffix = '<span class="WATERMARK END"> </span>'
    template = """<ac:structured-macro ac:name="info">
        <ac:rich-text-body>
        <p><span>{watermark}</span></p>
        </ac:rich-text-body>
        </ac:structured-macro>"""

    def __init__(self, watermark):
        super(WatermarkPageMutator, self).__init__()
        self.set_param('watermark', watermark)


class LinkPageMutator(TemplatePageMutator):
    template_prefix = '<span class="LINK BEGIN"> </span>'
    template_suffix = '<span class="LINK END"> </span>'
    template = """<ac:structured-macro ac:name="info">
        <ac:rich-text-body>
        <p><span><a href="{link}" _blank="true">{link}</a></span></p>
        </ac:rich-text-body>
        </ac:structured-macro>"""

    def __init__(self, link):
        super(LinkPageMutator, self).__init__()
        self.set_param('link', link)


class AnchorPageMutator(PageMutator):
    anchor_expression = None
    _title = u''
    _unused_title = u''

    def __init__(self, title, unused_title):
        if title:
            self._title = ''.join(title.split())
        if unused_title:
            self._unused_title = ''.join(unused_title.split())
        self.anchor_expression = re.compile(re.escape(self._unused_title))

    def mutate(self, page):
        page.body = self.anchor_expression.sub(self._title, page.body, re.I|re.U)
