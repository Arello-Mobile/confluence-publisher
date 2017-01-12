from sys import version_info
from base64 import b64encode
from getpass import getpass
import requests

PY3 = version_info.major >= 3


def base64(string):
    if PY3:
        return b64encode(string.encode('utf8')).decode('utf8')
    return b64encode(string)


def parse_authentication(auth=None, user=None, auth_type="basic"):
    if user is not None:
        password = getpass('Enter Confluence password:')
        if auth_type == "basic":
            return base64('%s:%s' % (user, password))
        else:
            s = requests.Session()
            s.auth = (user, password)
            return s

    return auth
