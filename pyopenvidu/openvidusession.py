"""OpenViduSession class."""
from typing import Iterator, List
from datetime import datetime
from requests_toolbelt.sessions import BaseUrlSession

from .exceptions import OpenViduSessionDoesNotExistsError, OpenViduConnectionDoesNotExistsError
from .openviduconnection import OpenViduConnection


class OpenViduSession(object):
    """
    This object represents an OpenVidu Session.
    A session is a group of users sharing communicating each other.
    """

    def __init__(self, session: BaseUrlSession, data: dict):
        """
        The constructor of this class is intended for internal use. Please use OpenVidu.get_session call to instantiate.

        :param session: The requests session object used for communication.
        :param data: The initial internal data stored of the session.
        """
        self._session = session
        self._data = data

    def fetch(self):
        """
        Updates every property of the OpenViduSession with the current status it has in OpenVidu Server. This is especially useful for getting the list of active connections to the OpenViduSession (get_connections()).
        To update every OpenViduSession object owned by OpenVidu object, call OpenVidu.fetch()

        :return: True if the OpenViduSession status has changed with respect to the server, False if not. This applies to any property or sub-property of the object

        """
        r = self._session.get(f"api/sessions/{self.id}")

        if r.status_code == 404:
            self._data = {}
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()

        is_changed = self._data != r.json()

        if is_changed:
            self._data = r.json()

        return is_changed

    def close(self):
        """
        Gracefully closes the Session: unpublishes all streams and evicts every participant.
        Further calls to this object will fail.
        """
        r = self._session.delete(f"/api/sessions/{self.id}")

        if r.status_code == 404:
            self._data = {}
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()
        self._data = {}

    @property
    def is_valid(self) -> bool:
        """
        Checks if this session still existed on the server by the last call to fetch().

        :return: True if the session exists. False otherwise.
        """
        return bool(self._data)

    def generate_token(self, role: str = 'PUBLISHER', data: str = None, video_max_recv_bandwidth: int = None,
                       video_min_recv_bandwidth: int = None, video_max_send_bandwidth: int = None,
                       video_min_send_bandwidth: int = None, allowed_filters: list = None) -> str:
        """
        Gets a new token associated to Session.

        In the video bandwidth settings 0 means unconstrained. Setting any of them (other than None) overrides the values configured in for the server.

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
        if not self._data:  # Fail early... and always
            raise OpenViduSessionDoesNotExistsError()

        # Prepare parameters

        if role not in ['SUBSCRIBER', 'PUBLISHER', 'MODERATOR']:
            raise ValueError(f"Role must be any of SUBSCRIBER, PUBLISHER or MODERATOR, not {role}")

        parameters = {"session": self.id, "role": role}

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
    def connections(self) -> Iterator[OpenViduConnection]:
        """
        Returns the list of active connections to the session.

        :return: A generator for OpenViduConnection objects.
        """
        if not self._data:
            raise OpenViduSessionDoesNotExistsError()

        for connection_info in self._data['connections']['content']:
            yield OpenViduConnection(self._session, self.id, connection_info)

    def get_connection(self, connection_id: str) -> OpenViduConnection:
        """
        Get a currently active connection to the server.

        :param connection_id: Connection id.
        :return: A OpenViduConnection objects.
        """
        if not self._data:
            raise OpenViduSessionDoesNotExistsError()

        for connection_info in self._data['connections']['content']:
            if connection_info['connectionId'] == connection_id:
                return OpenViduConnection(self._session, self.id, connection_info)

        raise OpenViduConnectionDoesNotExistsError()

    def signal(self, type_: str = None, data: str = None, to: List[OpenViduConnection] = None):
        """
        Sends a signal to all participants in the session or specific connections if the `to` property defined.
        OpenViduConnection objects also implement this method.

        https://openvidu.io/docs/reference-docs/REST-API/#post-apisignal
        :param type_: Type of the signal. In the body example of the table above, only users subscribed to Session.on('signal:MY_TYPE') will trigger that signal. Users subscribed to Session.on('signal') will trigger signals of any type.
        :param data: Actual data of the signal.
        :param to: List of OpenViduConnection objects to which you want to send the signal. If this property is not set (None) the signal will be sent to all participants of the session.
        """
        if not self._data:  # Fail early... and always
            raise OpenViduSessionDoesNotExistsError()

        if to:
            recipient_list = [connection.id for connection in to]
        else:
            recipient_list = None

        parameters = {
            "session": self.id,
            "to": recipient_list,
            "type": type_,
            "data": data
        }

        parameters = {k: v for k, v in parameters.items() if v is not None}

        # send request
        r = self._session.post('api/signal', json=parameters)

        if r.status_code == 404:
            raise OpenViduSessionDoesNotExistsError()
        elif r.status_code == 400:
            raise ValueError()
        elif r.status_code == 406:
            raise OpenViduConnectionDoesNotExistsError()

        r.raise_for_status()

    @property
    def connection_count(self) -> int:
        """
        Get the number of active connections to the session.

        :return: The number of active connections.
        """
        if not self._data:
            raise OpenViduSessionDoesNotExistsError()

        return self._data['connections']['numberOfElements']

    @property
    def id(self) -> str:
        """
        :return: The ID of this session.
        """
        if not self._data:
            raise OpenViduSessionDoesNotExistsError()

        return self._data['sessionId']

    @property
    def created_at(self) -> datetime:
        """
        :return: datetime object when the session was created in UTC time.
        """
        return datetime.utcfromtimestamp(self._data['createdAt'] / 1000.0)

    @property
    def is_being_recorded(self) -> bool:
        """
        :return: True if the session is being recorded. False otherwise.
        """
        return self._data['recording']

    @property
    def media_mode(self) -> str:
        """
        :return: Media mode configured for the session ('ROUTED' or 'RELAYED').
        """
        return self._data['mediaMode']
