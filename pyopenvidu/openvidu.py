"""OpenVidu class."""
from typing import List

from requests_toolbelt.sessions import BaseUrlSession
from requests.auth import HTTPBasicAuth
from requests_toolbelt import user_agent

from . import __version__
from .exceptions import OpenViduSessionDoesNotExistsError
from .openvidusession import OpenViduSession


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

        self._openvidu_sessions = {}  # id:object
        self.fetch()  # initial fetch

    def fetch(self) -> bool:
        """
        Updates every property of every active Session with the current status they have in OpenVidu Server. After calling this method you can access the updated list of active sessions by calling get_sessions()

        :return: true if the Session status has changed with respect to the server, false if not. This applies to any property or sub-property of the object.
        """
        r = self._session.get("api/sessions")
        r.raise_for_status()

        current_data = [s._data for s in self._openvidu_sessions.values()]
        new_data = r.json()['content']

        is_changed = current_data != new_data

        if is_changed:
            # update, create valid streams
            valid_sessions = []
            for session_data in new_data:
                session_id = session_data['sessionId']
                valid_sessions.append(session_id)

                if session_id in self._openvidu_sessions.keys():
                    # Update is important, because the reference must be the same
                    self._openvidu_sessions[session_id]._data = session_data
                else:
                    self._openvidu_sessions[session_id] = OpenViduSession(self._session, session_data)

            # reset data of invalid streams
            for session_id, session in self._openvidu_sessions.items():
                if session_id not in valid_sessions:
                    session._data = {}

            # remove invalid sessions from list
            self._openvidu_sessions = {k: v for k, v in self._openvidu_sessions.items() if k in valid_sessions}

        return is_changed

    def get_sessions(self) -> List[OpenViduSession]:
        """
        Get a list of currently active sessions to the server.

        :return: A list of OpenViduSession objects.
        """
        return list(self._openvidu_sessions.values())

    def get_session(self, session_id: str) -> OpenViduSession:
        """
        Get a currently active session to the server.

        :param session_id: The ID of the session to acquire.
        :return: An OpenViduSession object.
        """
        if session_id not in self._openvidu_sessions:
            raise OpenViduSessionDoesNotExistsError()

        return self._openvidu_sessions[session_id]


    def get_session_count(self) -> int:
        """
        Get the number of active sessions on the server.

        :return: The number of active sessions.
        """
        return len(self._openvidu_sessions)

    def get_config(self) -> dict:
        """
        Get OpenVidu active configuration.

        Unlike session related calls. This call does not require prior calling of the fetch() method.
        Using this function will always result an API call to the backend.

        https://openvidu.io/docs/reference-docs/REST-API/#get-config
        :return: The exact response from the server as a dict.
        """
        r = self._session.get('config')
        r.raise_for_status()

        return r.json()
