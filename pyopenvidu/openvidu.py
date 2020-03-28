"""OpenVidu class."""
from typing import Iterator

from requests_toolbelt.sessions import BaseUrlSession
from requests.auth import HTTPBasicAuth
from requests_toolbelt import user_agent

from . import __version__
from .exceptions import OpenViduSessionDoesNotExistsError
from .openvidusession import OpenViduSession


class OpenVidu(object):
    """
    This object represents a OpenVidu server instance.
    """

    def __init__(self, url: str, secret: str):
        """

        :param url: The url to reach your OpenVidu Server instance. Typically something like https://localhost:4443/
        :param secret: Secret for your OpenVidu Server
        """
        self._session = BaseUrlSession(base_url=url)
        self._session.auth = HTTPBasicAuth('OPENVIDUAPP', secret)

        self._session.headers.update({
            'User-Agent': user_agent('PyOpenVidu', __version__)
        })

    def get_sessions(self) -> Iterator[OpenViduSession]:
        """
        Get a list of currently active sessions to the server.

        :return: A generator for OpenViduSession objects.
        """
        for session_info in self.get_sessions_info()['content']:
            session_id = session_info['sessionId']
            yield OpenViduSession(self._session, session_id)

    def get_session(self, session_id: str) -> OpenViduSession:
        """
        Get a currently active session to the server.

        :return: A OpenViduSession object.
        """
        # check for existence
        self.get_session_info(session_id)  # This call is used to raise exceptions if the session does not exists
        return OpenViduSession(self._session, session_id)

    def get_session_info(self, session_id: str) -> dict:
        """
        Get the raw data returned by the server for a session.

        https://openvidu.io/docs/reference-docs/REST-API/#get-apisessionsltsession_idgt
        :return: The exact response from the server as a dict.
        """
        r = self._session.get(f'api/sessions/{session_id}')

        if r.status_code == 404:
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()

        return r.json()

    def get_sessions_info(self) -> dict:
        """
        Get the raw data returned by the server for sessions.

        https://openvidu.io/docs/reference-docs/REST-API/#get-apisessions
        :return: The exact response from the server as a dict.
        """
        r = self._session.get('api/sessions')
        r.raise_for_status()

        return r.json()

    def get_session_count(self) -> int:
        """
        Get the number of active sessions on the server.

        :return: The number of active sessions
        """
        return self.get_sessions_info()['numberOfElements']

    def get_config(self) -> dict:
        """
        Get OpenVidu active configuration.

        https://openvidu.io/docs/reference-docs/REST-API/#get-config
        :return: The exact response from the server as a dict.
        """
        r = self._session.get('config')
        r.raise_for_status()

        return r.json()
