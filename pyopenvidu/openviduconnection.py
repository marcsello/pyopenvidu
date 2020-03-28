"""OpenViduConnection class."""

from requests_toolbelt.sessions import BaseUrlSession
from .exceptions import OpenViduConnectionDoesNotExistsError, OpenViduSessionDoesNotExistsError


class OpenViduConnection(object):
    """
    This object represents an OpenVidu Connection.
    This is a connection between an user and a session.
    """

    def __init__(self, session: BaseUrlSession, session_id: str, connection_id: str):
        self._session = session
        self._session_id = session_id
        self._id = connection_id

    def force_disconnect(self):
        """
        Forces the user represented by connection to leave the session.

        https://openvidu.io/docs/reference-docs/REST-API/#delete-apisessionsltsession_idgtconnectionltconnection_idgt
        """
        r = self._session.delete(f"api/sessions/{self._session_id}/connection/{self._id}")
        if r.status_code == 404:
            raise OpenViduConnectionDoesNotExistsError()
        if r.status_code == 400:
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()

    def get_info(self) -> dict:
        """
        Get the raw data returned by the server for the client.
        This function returns a subset of the session info. This is implemented for consistency.

        https://openvidu.io/docs/reference-docs/REST-API/#get-apisessionsltsession_idgt
        :return: subset of the exact response from the server as a dict.
        """
        r = self._session.get(f'api/sessions/{self._session_id}')

        if r.status_code == 404:
            raise OpenViduSessionDoesNotExistsError()

        r.raise_for_status()

        for connection_info in r.json()['connections']['content']:
            if connection_info['connectionId'] == self._id:
                return connection_info

        raise OpenViduConnectionDoesNotExistsError()

    @property
    def id(self) -> str:
        return self._id

    @property
    def session_id(self) -> str:
        return self._session_id
