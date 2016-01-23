import json


def load(stream):
    return json.load(stream)


def dump(data, stream):
    return json.dump(data, stream)
