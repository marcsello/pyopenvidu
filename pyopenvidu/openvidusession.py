"""OpenViduSession class."""
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from requests_toolbelt.sessions import BaseUrlSession

from .exceptions import OpenViduSessionDoesNotExistsError, OpenViduConnectionDoesNotExistsError, OpenViduError
from .openviduconnection import OpenViduConnection, OpenViduWEBRTCConnection, OpenViduIPCAMConnection


@dataclass(frozen=False, init=False)
class OpenViduSession(object):
    """
    This object represents an OpenVidu Session.
    A session is a group of users sharing communicating each other.
    """

    id: str
    created_at: datetime
    is_being_recorded: bool
    media_mode: str
    connections: List[OpenViduConnection]
    is_valid: bool

    def __get_proper_connection_type(self, connection_info) -> OpenViduConnection:
        if connection_info['type'] == 'WEBRTC':
            return OpenViduWEBRTCConnection(self._session, connection_info)
        elif connection_info['type'] == 'IPCAM':
            return OpenViduIPCAMConnection(self._session, connection_info)
        else:
            raise RuntimeError("Unknown connection type")

    def __update_from_data(self, data: dict):
        self.id = data['id']
        self.created_at = datetime.utcfromtimestamp(data['createdAt'] / 1000.0)
        self.is_being_recorded = data['recording']
        self.media_mode = data['mediaMode']

        connections = []
        for connection_info in data['connections']['content']:
            connections.append(
                self.__get_proper_connection_type(connection_info)
            )
        self.connections = connections
        self.is_valid = True

    def __init__(self, session: BaseUrlSession, data: dict):
        """
        This is meant for internal use, thus you should not call it.
        Use `OpenVidu.get_session` to get an instance of this class.
        """

        self._session = session

        self.__update_from_data(data)
        self._last_fetch_result = data

    def fetch(self):
        """
        Updates every property of the OpenViduSession with the current status it has in OpenVidu Server. This is especially useful for getting the list of active connections to the OpenViduSession trough the `connections` property.

        :return: True if the OpenViduSession status has changed with respect to the server, False if not. This applies to any property or sub-property of the object
        """

        r = self._session.get(f"sessions/{self.id}")

        if r.status_code == 404:
            self.is_valid = False
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()

        new_data = r.json()
        is_changed = self._last_fetch_result != new_data

        if is_changed:
            self.__update_from_data(r.json())
            self._last_fetch_result = new_data

        return is_changed

    def close(self):
        """
        Gracefully closes the Session: unpublishes all streams and evicts every participant.
        Further calls to this object will fail.
        """

        r = self._session.delete(f"sessions/{self.id}")

        if r.status_code == 404:
            self.is_valid = False
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()
        self.is_valid = False

    def get_connection(self, connection_id: str) -> OpenViduConnection:
        """
        Get a currently active connection to the server.

        :param connection_id: Connection id.
        :return: A OpenViduConnection objects.
        """

        for connection in self.connections:
            if connection.id == connection_id:
                return connection

        raise OpenViduConnectionDoesNotExistsError()

    def signal(self, type_: str = None, data: str = None, to: Optional[List[OpenViduConnection]] = None):
        """
        Sends a signal to all participants in the session or specific connections if the `to` property defined.
        OpenViduConnection objects also implement this method.

        https://docs.openvidu.io/en/2.16.0/reference-docs/REST-API/#post-openviduapisignal

        :param type_: Type of the signal. In the body example of the table above, only users subscribed to Session.on('signal:MY_TYPE') will trigger that signal. Users subscribed to Session.on('signal') will trigger signals of any type.
        :param data: Actual data of the signal.
        :param to: List of OpenViduConnection objects to which you want to send the signal. If this property is not set (None) the signal will be sent to all participants of the session.
        """

        if not self.is_valid:  # Fail early... and always
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
        r = self._session.post('signal', json=parameters)

        if r.status_code == 404:
            self.is_valid = False
            raise OpenViduSessionDoesNotExistsError()
        elif r.status_code == 400:
            raise ValueError()
        elif r.status_code == 406:
            self.is_valid = False
            raise OpenViduConnectionDoesNotExistsError()

        r.raise_for_status()

    def __create_connection(self, parameters: dict) -> dict:
        r = self._session.post(f'sessions/{self.id}/connection', json=parameters)

        if r.status_code == 404:
            self.is_valid = False
            raise OpenViduSessionDoesNotExistsError()
        elif r.status_code == 400:
            raise ValueError()
        elif r.status_code == 500:
            raise OpenViduError(r.content)

        return r.json()

    def create_webrtc_connection(self, role: str = 'PUBLISHER', data: str = None, video_max_recv_bandwidth: int = None,
                                 video_min_recv_bandwidth: int = None, video_max_send_bandwidth: int = None,
                                 video_min_send_bandwidth: int = None,
                                 allowed_filters: list = None) -> OpenViduWEBRTCConnection:
        """
        Creates a new Connection object of WEBRTC (Regular user) type to the session.

        In the video bandwidth settings 0 means unconstrained. Setting any of them (other than None) overrides the values configured in for the server.

        https://docs.openvidu.io/en/2.16.0/reference-docs/REST-API/#post-openviduapisessionsltsession_idgtconnection

        :param role: Allowed values: `SUBSCRIBER`, `PUBLISHER` or `MODERATOR`
        :param data: metadata associated to this token (usually participant's information)
        :param video_max_recv_bandwidth: Maximum number of Kbps that the client owning the token will be able to receive from Kurento Media Server.
        :param video_min_recv_bandwidth: Minimum number of Kbps that the client owning the token will try to receive from Kurento Media Server.
        :param video_max_send_bandwidth: Maximum number of Kbps that the client owning the token will be able to send to Kurento Media Server.
        :param video_min_send_bandwidth: Minimum number of Kbps that the client owning the token will try to send to Kurento Media Server.
        :param allowed_filters: Array of strings containing the names of the filters the user owning the token will be able to apply.
        :return: An OpenVidu connection object represents the newly created connection.
        """

        if not self.is_valid:  # Fail early... and always
            raise OpenViduSessionDoesNotExistsError()

        # Prepare parameters

        if role not in ['SUBSCRIBER', 'PUBLISHER', 'MODERATOR']:
            raise ValueError(f"Role must be any of SUBSCRIBER, PUBLISHER or MODERATOR, not {role}")

        parameters = {
            "type": "WEBRTC",
            "role": role
        }

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

        response = self.__create_connection(parameters)
        new_connection = OpenViduWEBRTCConnection(self._session, response)
        self.connections.append(new_connection)
        return new_connection

    def create_ipcam_connection(self, rtsp_uri: str, data: str = None, adaptive_bitrate: bool = None,
                                only_play_with_subscribers: bool = None,
                                network_cache: int = None) -> OpenViduIPCAMConnection:
        """
        Publishes a new IPCAM rtsp stream to the session.

        Unlike `OpenVidu.create_session` this method does not call fetch() automatically, since the server returns enough data to construct the connection object.
        Keep in mind, that if you want the newly created Connection to appear in the `connections` list, you should call fetch() before accessing the list!

        https://docs.openvidu.io/en/2.16.0/reference-docs/REST-API/#post-openviduapisessionsltsession_idgtconnection

        :param rtsp_uri: RTSP URI of the IP camera. For example: `rtsp://your.camera.ip:7777/path`.
        :param data: Metadata you want to associate to the camera's participant.
        :param adaptive_bitrate: Whether to use adaptive bitrate or not.
        :param only_play_with_subscribers: Enable the IP camera stream only when some user is subscribed to it.
        :param network_cache: Size of the buffer of the endpoint receiving the IP camera's stream, in milliseconds.
        :return: An OpenVidu connection object represents the newly created connection.
        """

        if not self.is_valid:  # Fail early... and always
            raise OpenViduSessionDoesNotExistsError()

        parameters = {
            "type": "IPCAM",
            "data": data,
            "rtspUri": rtsp_uri,
            "adaptativeBitrate": adaptive_bitrate,
            "onlyPlayWithSubscribers": only_play_with_subscribers,
            "networkCache": network_cache
        }

        parameters = {k: v for k, v in parameters.items() if v is not None}

        response = self.__create_connection(parameters)
        new_connection = OpenViduIPCAMConnection(self._session, response)
        self.connections.append(new_connection)
        return new_connection

    @property
    def connection_count(self) -> int:
        """
        Get the number of active connections to the session.

        :return: The number of active connections.
        """

        return len(self.connections)
