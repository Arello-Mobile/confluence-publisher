import yaml
from collections import OrderedDict
import six


class OrderedDumper(yaml.Dumper):
    pass


def _dict_representer(dumper, data):
    return dumper.represent_dict(six.iteritems(data))

OrderedDumper.add_representer(OrderedDict, _dict_representer)


def load(stream):
    return yaml.load(stream)


def dump(data, stream=None):
    return yaml.dump(data, stream=stream, Dumper=OrderedDumper, default_flow_style=False)
