"""Main module."""
from requests_toolbelt.sessions import BaseUrlSession
from requests.auth import HTTPBasicAuth
from requests_toolbelt import user_agent
from . import __version__


class OpenVidu(object):

    def __init__(self, url: str, secret: str):
        self._session = BaseUrlSession(base_url=url)
        self._session.auth = HTTPBasicAuth('OPENVIDUAPP', secret)

        self._session.headers.update({
            'User-Agent': user_agent('PyOpenVidu', __version__)
        })

    def get_config(self):
        r = self._session.get('config')
        r.raise_for_status()

        return r.json()
