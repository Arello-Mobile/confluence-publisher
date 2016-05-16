import re


class PageMutator(object):

    def apply_forward(self, page):
        raise NotImplemented()

    def apply_backward(self, page):
        raise NotImplemented()


class TemplatePageMutator(PageMutator):
    template_prefix = None
    template_suffix = None
    template = None

    def __init__(self):
        self.template_params = {}

    def set_param(self, name, value):
        self.template_params[name] = value

    def apply_forward(self, page):
        page.body = self.template_prefix + self.template.format(**self.template_params) + self.template_suffix + page.body

    def apply_backward(self, page):
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
    _old_title = u''

    def __init__(self, old_title):
        if old_title:
            self._old_title = ''.join(old_title.split())
            self.anchor_expression = re.compile(re.escape(self._old_title))

    def apply_forward(self, page):
        if not page.title or not page.body or not self.anchor_expression:
            return
        _title = ''.join(page.title.split())
        page.body = self.anchor_expression.sub(_title, page.body, re.I|re.U)

    def apply_backward(self, page):
        pass
