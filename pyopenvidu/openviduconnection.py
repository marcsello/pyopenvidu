"""OpenViduConnection class."""
from typing import List, Optional
from requests_toolbelt.sessions import BaseUrlSession
from dataclasses import dataclass
from .exceptions import OpenViduConnectionDoesNotExistsError, OpenViduSessionDoesNotExistsError
from datetime import datetime
from .openvidupublisher import OpenViduPublisher
from .openvidusubscriber import OpenViduSubscriber


# Notice: Frozen should be changed to True in later versions of Python3 where a nice method for custom initializer is implemented
@dataclass(init=False, frozen=False)
class OpenViduConnection(object):
    id: str
    type: str
    session_id: str
    created_at: datetime
    active_at: datetime
    platform: str
    server_data: Optional[str]
    publishers: List[OpenViduPublisher]
    subscribers: List[OpenViduSubscriber]

    def _update_from_data(self, data: dict):
        # set property
        self.id = data['connectionId']
        self.type = data['type']  # Either IPCAM or WEBRTC
        self.session_id = data['sessionId']
        self.created_at = datetime.utcfromtimestamp(data['createdAt'] / 1000.0)
        self.active_at = datetime.utcfromtimestamp(data['activeAt'] / 1000.0)
        self.platform = data['platform']
        self.server_data = data.get('serverData', None)

        # set publishers
        publishers = []
        for publisher_data in data['publishers']:
            publishers.append(OpenViduPublisher(self._session, self.session_id, publisher_data))

        # set subscribers
        subscribers = []
        for subscriber_data in data['subscribers']:
            subscribers.append(OpenViduSubscriber(self._session, self.session_id, subscriber_data))

        self.publishers = publishers
        self.subscribers = subscribers

        # Specific properties will be set in the inherited functions

    def __init__(self, session: BaseUrlSession, data: dict):
        """
        This is meant for internal use, thus you should not call it.
        Use `OpenViduSession.connections` to get an instance of this class.
        """

        self._session = session
        self._update_from_data(data)

    def force_disconnect(self):
        """
        Forces the disconnection from the session.
        Remember to call fetch() after this call to fetch the current actual properties of the Session from OpenVidu Server!

        https://docs.openvidu.io/en/2.12.0/reference-docs/REST-API/#delete-apisessionsltsession_idgtconnectionltconnection_idgt
        """
        r = self._session.delete(f"sessions/{self.session_id}/connection/{self.id}")
        if r.status_code == 404:
            raise OpenViduConnectionDoesNotExistsError()
        if r.status_code == 400:
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()

    def signal(self, type_: str = None, data: str = None):
        """
        Sends a signal to this connection.

        https://docs.openvidu.io/en/2.12.0/reference-docs/REST-API/#post-apisignal

        :param type_: Type of the signal. In the body example of the table above, only users subscribed to Session.on('signal:MY_TYPE') will trigger that signal. Users subscribed to Session.on('signal') will trigger signals of any type.
        :param data: Actual data of the signal.
        """

        parameters = {
            "session": self.session_id,
            "to": [self.id],
            "type": type_,
            "data": data
        }

        parameters = {k: v for k, v in parameters.items() if v is not None}

        # send request
        r = self._session.post('signal', json=parameters)

        if r.status_code == 404:
            raise OpenViduSessionDoesNotExistsError()
        elif r.status_code == 400:
            raise ValueError()
        elif r.status_code == 406:
            raise OpenViduConnectionDoesNotExistsError()

        r.raise_for_status()

    def force_unpublish_all_streams(self):
        """
        Forces the user to unpublish all of their Stream. OpenVidu Browser will trigger the proper events on the client-side (streamDestroyed) with reason set to "forceUnpublishByServer".
        After this call, the instace of the object, should be considered invalid.
        Remember to call fetch() after this call to fetch the current actual properties of the Session from OpenVidu Server!

        https://docs.openvidu.io/en/2.12.0/reference-docs/REST-API/#delete-apisessionsltsession_idgtstreamltstream_idgt
        """
        for publisher in self.publishers:
            publisher.force_unpublish()


# Notice: Frozen should be changed to True in later versions of Python3 where a nice method for custom initializer is implemented
@dataclass(init=False, frozen=False)
class OpenViduWEBRTCConnection(OpenViduConnection):
    """
    This object represents an OpenVidu WEBRTC type of Connection.
    This is a connection between an user and a session.
    """

    token: Optional[str]
    client_data: Optional[str]
    role: str
    kurento_options: dict

    def _update_from_data(self, data: dict):
        super()._update_from_data(data)  # Set the common properties
        self.token = data.get('token', None)
        self.client_data = data.get('clientData', None)
        self.role = data['role']
        self.kurento_options = data['kurentoOptions']


# Notice: Frozen should be changed to True in later versions of Python3 where a nice method for custom initializer is implemented
@dataclass(init=False, frozen=False)
class OpenViduIPCAMConnection(OpenViduConnection):
    """
    This object represents an OpenVidu IPCAM type of Connection.
    This is a connection between an IPCAM and a session.
    """
    rtsp_uri: str
    adaptive_bitrate: bool
    only_play_with_subscribers: bool
    network_cache: int

    def _update_from_data(self, data: dict):
        super()._update_from_data(data)  # Set the common properties
        self.rtsp_uri = data['rtspUri']
        self.adaptive_bitrate = data['adaptativeBitrate']
        self.only_play_with_subscribers = data['onlyPlayWithSubscribers']
        self.network_cache = data['networkCache']
