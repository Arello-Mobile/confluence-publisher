# import random
#
# from conf_publisher.confluence import ConfluenceManager
#
#
# class FakePagePublisher(ConfluenceManager):
#     def publish(self, title, body, content_id=None, parent_id=None):
#         if content_id is not None:
#             return content_id
#
#         if parent_id is not None:
#             return parent_id + random.randint(10000, 100000)
#
#         raise ValueError('content_id is none')
#
#
# class FakeAttachmentPublisher(ConfluenceManager):
#     def publish(self, content_id, filename):
#         return random.randint(10000, 100000)
