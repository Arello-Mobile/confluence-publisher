from sys import version_info
from getpass import getpass
from base64 import b64encode, b64decode
from requests.auth import HTTPBasicAuth, AuthBase

PY3 = version_info.major >= 3


def base64(string):
    if PY3:
        return b64encode(string.encode('utf8')).decode('utf8')
    return b64encode(string)


class HTTPBasicAuthWithToken(AuthBase):
    """Interface similar HTTPBasicAuth."""

    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        b = bytes(self.token, 'utf8')
        username, password = b64decode(b).decode('utf8').split(':')
        return all([
            username == getattr(other, 'username', None),
            password == getattr(other, 'password', None)
        ])

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = 'Basic {}'.format(self.token)
        return r


def parse_authentication(auth=None, user=None):
    if user is not None:
        password = getpass()
        return HTTPBasicAuth(user, password)
    return HTTPBasicAuthWithToken(auth)
