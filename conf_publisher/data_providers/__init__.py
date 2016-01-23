class DataProvider(object):

    def get_source(self, filename):
        raise NotImplemented()

    def get_source_data(self, filename):
        raise NotImplemented()

    def get_image(self, filename):
        raise NotImplemented()

    def get_image_stream(self, filename):
        raise NotImplemented()

    def get_attachment(self, filename):
        raise NotImplemented()

    def get_attachment_stream(self, filename):
        raise NotImplemented()
