"""OpenViduConnection class."""
from typing import List
from requests_toolbelt.sessions import BaseUrlSession
from dataclasses import dataclass
from .exceptions import OpenViduConnectionDoesNotExistsError, OpenViduSessionDoesNotExistsError
from datetime import datetime
from .openvidupublisher import OpenViduPublisher
from .openvidusubscriber import OpenViduSubscriber


# Notice: Frozen should be changed to True in later versions of Python3 where a nice method for custom initializer is implemented
@dataclass(init=False, frozen=False)
class OpenViduConnection(object):
    """
    This object represents an OpenVidu Connection.
    This is a connection between an user and a session.
    """
    id: str
    session_id: str
    created_at: datetime
    publishers: List[OpenViduPublisher]
    subscribers: List[OpenViduSubscriber]
    platform: str
    token: str
    role: str
    server_data: str
    client_data: str

    def __init__(self, session: BaseUrlSession, session_id: str, data: dict):
        self._session = session

        # set property
        self.id = data['connectionId']
        self.session_id = session_id
        self.created_at = datetime.utcfromtimestamp(data['createdAt'] / 1000.0)
        self.platform = data['platform']
        self.token = data['token']
        self.role = data['role']
        self.server_data = data['serverData']
        self.client_data = data['clientData']

        # set publishers
        publishers = []
        for publisher_data in data['publishers']:
            publishers.append(OpenViduPublisher(session, session_id, publisher_data))

        # set subscribers
        subscribers = []
        for subscriber_data in data['subscribers']:
            subscribers.append(OpenViduSubscriber(session, session_id, subscriber_data))

        self.publishers = publishers
        self.subscribers = subscribers

    def force_disconnect(self):
        """
        Forces the user represented by connection to leave the session.
        Remember to call fetch() after this call to fetch the current actual properties of the Session from OpenVidu Server!

        https://openvidu.io/docs/reference-docs/REST-API/#delete-apisessionsltsession_idgtconnectionltconnection_idgt
        """
        r = self._session.delete(f"api/sessions/{self.session_id}/connection/{self.id}")
        if r.status_code == 404:
            raise OpenViduConnectionDoesNotExistsError()
        if r.status_code == 400:
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()

    def signal(self, type_: str = None, data: str = None):
        """
        Sends a signal to this connection.

        https://openvidu.io/docs/reference-docs/REST-API/#post-apisignal
        :param type_: Type of the signal. In the body example of the table above, only users subscribed to Session.on('signal:MY_TYPE') will trigger that signal. Users subscribed to Session.on('signal') will trigger signals of any type.
        :param data: Actual data of the signal.
        :param to: List of OpenViduConnection objects to which you want to send the signal. If this property is not set (None) the signal will be sent to all participants of the session.
        """

        parameters = {
            "session": self.session_id,
            "to": [self.id],
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

    def force_unpublish_all_streams(self):
        """
        Forces the user to unpublish all of their Stream. OpenVidu Browser will trigger the proper events on the client-side (streamDestroyed) with reason set to "forceUnpublishByServer".
        After this call, the instace of the object, should be considered invalid.
        Remember to call fetch() after this call to fetch the current actual properties of the Session from OpenVidu Server!

        https://openvidu.io/docs/reference-docs/REST-API/#delete-apisessionsltsession_idgtstreamltstream_idgt
        """
        for publisher in self.publishers:
            publisher.force_unpublish()
