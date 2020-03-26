"""Main module."""
from typing import Optional, Iterator

from requests_toolbelt.sessions import BaseUrlSession
from requests.auth import HTTPBasicAuth
from requests_toolbelt import user_agent

from . import __version__


class OpenViduConnection(object):
    """
    This object represents an OpenVidu Connection.
    This is a connection between an user and a session.
    """

    def __init__(self, session: BaseUrlSession, connection_id: str):
        self._session = session
        self._id = connection_id

    @property
    def id(self) -> str:
        return self._id


class OpenViduSession(object):
    """
    This object represents an OpenVidu Session.
    A session is a group of users sharing communicating each other.
    """

    def __init__(self, session: BaseUrlSession, session_id: str):
        """
        The constructor of this class is intended for internal use. Please use OpenVidu.get_session call to instantiate.

        :param session: The requests session object used for communication.
        :param session_id: The ID of the session this object is going to represent.
        """
        self._session = session
        self._id = session_id

    @property
    def id(self) -> str:
        return self._id


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
        Get a list of currently active sessions from the server.

        :return: A generator for OpenViduSession objects.
        """
        r = self._session.get('api/sessions')
        r.raise_for_status()

        for session_info in r.json()['content']:
            session_id = session_info['sessionId']
            yield OpenViduSession(self._session, session_id)

    def get_session(self, session_id: str) -> Optional[OpenViduSession]:
        """
        Get a currently active session from the server.
        Returns None if the session does not exists.

        :return: A OpenViduSession object.
        """
        # check for existence
        r = self._session.get(f'api/sessions/{session_id}')

        if r.status_code == 404:
            return None

        r.raise_for_status()

        return OpenViduSession(self._session, session_id)

    def get_session_info(self, session_id: str) -> dict:
        """
        Get the raw data returned by the server for a session.

        https://openvidu.io/docs/reference-docs/REST-API/#get-apisessionsltsession_idgt
        :return: The exact response from the server as a dict.
        """
        r = self._session.get(f'api/sessions/{session_id}')
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

    def get_config(self) -> dict:
        """
        Get OpenVidu active configuration.

        https://openvidu.io/docs/reference-docs/REST-API/#get-config
        :return: The exact response from the server as a dict.
        """
        r = self._session.get('config')
        r.raise_for_status()

        return r.json()
