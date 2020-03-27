"""OpenViduConnection class."""

from requests_toolbelt.sessions import BaseUrlSession


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
