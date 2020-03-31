"""OpenViduConnection class."""
from typing import List
from requests_toolbelt.sessions import BaseUrlSession
from dataclasses import dataclass
from .exceptions import OpenViduConnectionDoesNotExistsError, OpenViduSessionDoesNotExistsError
from datetime import datetime
from .openvidupublisher import OpenViduPublisher


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

        self.publishers = publishers

    def force_disconnect(self):
        """
        Forces the user represented by connection to leave the session.

        https://openvidu.io/docs/reference-docs/REST-API/#delete-apisessionsltsession_idgtconnectionltconnection_idgt
        """
        r = self._session.delete(f"api/sessions/{self.session_id}/connection/{self.id}")
        if r.status_code == 404:
            raise OpenViduConnectionDoesNotExistsError()
        if r.status_code == 400:
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()
