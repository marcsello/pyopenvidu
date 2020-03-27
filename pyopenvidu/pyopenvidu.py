"""Main module."""
from typing import Iterator

from requests_toolbelt.sessions import BaseUrlSession
from requests.auth import HTTPBasicAuth
from requests_toolbelt import user_agent

from . import __version__
from .exceptions import OpenViduSessionDoesNotExistsError


class OpenViduConnection(object):
    """
    This object represents an OpenVidu Connection.
    This is a connection between an user and a session.
    """

    def __init__(self, session: BaseUrlSession, session_id: str, connection_id: str):
        self._session = session
        self._session_id = session_id
        self._id = connection_id

    @property
    def id(self) -> str:
        return self._id

    @property
    def session_id(self) -> str:
        return self._session_id


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

    def is_valid(self) -> bool:
        """
        Checks if this session still exists on the server.
        :return: True if the session exists. False otherwise.
        """
        r = self._session.get(f'api/sessions/{self._id}')

        return r.status_code == 200

    def close(self):
        """
        Gracefully closes the Session: unpublishes all streams and evicts every participant.
        Further calls to this object will fail.
        """
        r = self._session.delete(f"/api/sessions/{self.id}")

        if r.status_code == 404:
            raise OpenViduSessionDoesNotExistsError()

    def get_info(self) -> dict:
        """
        Get the raw data returned by the server for a session.

        https://openvidu.io/docs/reference-docs/REST-API/#get-apisessionsltsession_idgt
        :return: The exact response from the server as a dict.
        """
        r = self._session.get(f'api/sessions/{self._id}')

        if r.status_code == 404:
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()

        return r.json()

    def generate_token(self, role: str = 'PUBLISHER', data: str = None, video_max_recv_bandwidth: int = None,
                       video_min_recv_bandwidth: int = None, video_max_send_bandwidth: int = None,
                       video_min_send_bandwidth: int = None, allowed_filters: list = None) -> str:
        """
        Gets a new token associated to Session.

        In the video bandwidth settings 0 means unconstrained. Setting any of them overrides the values configured in for the server

        https://openvidu.io/docs/reference-docs/REST-API/#post-apitokens
        :param role: Allowed values: `SUBSCRIBER`, `PUBLISHER` or `MODERATOR`
        :param data: metadata associated to this token (usually participant's information)
        :param video_max_recv_bandwidth: Maximum number of Kbps that the client owning the token will be able to receive from Kurento Media Server.
        :param video_min_recv_bandwidth: Minimum number of Kbps that the client owning the token will try to receive from Kurento Media Server.
        :param video_max_send_bandwidth: Maximum number of Kbps that the client owning the token will be able to send to Kurento Media Server.
        :param video_min_send_bandwidth: Minimum number of Kbps that the client owning the token will try to send to Kurento Media Server.
        :param allowed_filters: Array of strings containing the names of the filters the user owning the token will be able to apply.
        :return: The token as String.
        """
        # Prepare parameters

        if role not in ['SUBSCRIBER', 'PUBLISHER', 'MODERATOR']:
            raise ValueError(f"Role must be any of SUBSCRIBER, PUBLISHER or MODERATOR, not {role}")

        parameters = {"session": self._id, "role": role}

        if data:
            parameters['data'] = data

        kurento_options = {
            "videoMaxRecvBandwidth": video_max_recv_bandwidth,
            "videoMinRecvBandwidth": video_min_recv_bandwidth,
            "videoMaxSendBandwidth": video_max_send_bandwidth,
            "videoMinSendBandwidth": video_min_send_bandwidth,
            "allowedFilters": allowed_filters
        }

        kurento_options = {k: v for k, v in kurento_options.items() if v is not None}

        if kurento_options:
            parameters['kurentoOptions'] = kurento_options

        # send request
        r = self._session.post('api/tokens', json=parameters)

        if r.status_code == 404:
            raise OpenViduSessionDoesNotExistsError()
        elif r.status_code == 400:
            raise ValueError()

        return r.json()['token']

    @property
    def id(self) -> str:
        """

        :return: The ID of this session.
        """
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

    def get_session(self, session_id: str) -> OpenViduSession:
        """
        Get a currently active session from the server.
        Returns None if the session does not exists.

        :return: A OpenViduSession object.
        """
        # check for existence
        r = self._session.get(f'api/sessions/{session_id}')

        if r.status_code == 404:
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()

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
