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
