"""OpenViduConnection class."""

from requests_toolbelt.sessions import BaseUrlSession
from .exceptions import OpenViduConnectionDoesNotExistsError, OpenViduSessionDoesNotExistsError


class OpenViduConnection(object):
    """
    This object represents an OpenVidu Connection.
    This is a connection between an user and a session.
    """

    def __init__(self, session: BaseUrlSession, session_id: str, data: dict):
        self._session = session
        self._session_id = session_id
        self._data = data

    def force_disconnect(self):
        """
        Forces the user represented by connection to leave the session.

        https://openvidu.io/docs/reference-docs/REST-API/#delete-apisessionsltsession_idgtconnectionltconnection_idgt
        """
        r = self._session.delete(f"api/sessions/{self._session_id}/connection/{self.id}")
        if r.status_code == 404:
            raise OpenViduConnectionDoesNotExistsError()
        if r.status_code == 400:
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()

    @property
    def id(self) -> str:
        """

        :return: The ID of the connection this object represents.
        """
        return self._data['connectionId']

    @property
    def session_id(self) -> str:
        """

        :return: The ID of the session this Connection lives in.
        """
        return self._session_id
