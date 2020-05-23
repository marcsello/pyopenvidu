"""OpenVidu class."""
from typing import List, Union
from functools import partial
from threading import RLock

from requests_toolbelt.sessions import BaseUrlSession
from requests.auth import HTTPBasicAuth
from requests_toolbelt import user_agent

from . import __version__
from .exceptions import OpenViduSessionDoesNotExistsError, OpenViduSessionExistsError
from .openvidusession import OpenViduSession


class OpenVidu(object):
    """
    This object represents a OpenVidu server instance.
    """

    def __init__(self, url: str, secret: str, initial_fetch: bool = True, timeout: Union[int, tuple, None] = None):
        """
        :param url: The url to reach your OpenVidu Server instance. Typically something like https://localhost:4443/
        :param secret: Secret for your OpenVidu Server
        :param initial_fetch: Enable the initial fetching on object creation. Defaults to `True`. If set to `False` a `fetc()` must be called before doing anything with the object. In most scenarios you won't need to change this.
        :param timeout: Set timeout to all Requests to the OpenVidu server. Default: None = No timeout. See https://2.python-requests.org/en/latest/user/advanced/#timeouts for possible values.
        """
        self._session = BaseUrlSession(base_url=url)
        self._session.auth = HTTPBasicAuth('OPENVIDUAPP', secret)

        self._session.headers.update({
            'User-Agent': user_agent('PyOpenVidu', __version__)
        })

        self._session.request = partial(self._session.request, timeout=timeout)

        self._lock = RLock()

        self._openvidu_sessions = {}  # id:object

        if initial_fetch:
            self.fetch()  # initial fetch

    def fetch(self) -> bool:
        """
        Updates every property of every active Session with the current status they have in OpenVidu Server. After calling this method you can access the updated list of active sessions by calling get_sessions()

        :return: true if the Session status has changed with respect to the server, false if not. This applies to any property or sub-property of the object.
        """
        with self._lock:
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
                        self._openvidu_sessions[session_id] = OpenViduSession(self._session, self._lock, session_data)

                # reset data of invalid streams
                for session_id, session in self._openvidu_sessions.items():
                    if session_id not in valid_sessions:
                        session._data = {}

                # remove invalid sessions from list
                self._openvidu_sessions = {k: v for k, v in self._openvidu_sessions.items() if k in valid_sessions}

            return is_changed

    def get_session(self, session_id: str) -> OpenViduSession:
        """
        Get a currently active session to the server.

        :param session_id: The ID of the session to acquire.
        :return: An OpenViduSession object.
        """
        with self._lock:
            if session_id not in self._openvidu_sessions:
                raise OpenViduSessionDoesNotExistsError()

            session = self._openvidu_sessions[session_id]

            if not session.is_valid:
                raise OpenViduSessionDoesNotExistsError()

            return session

    def create_session(self, custom_session_id: str = None, media_mode: str = None) -> OpenViduSession:
        """
        Creates a new OpenVidu session.

        This method calls fetch() automatically since the server does not return the proper data to construct the OpenViduSession object.

        https://docs.openvidu.io/en/2.12.0/reference-docs/REST-API/#post-apisessions

        :param custom_session_id: You can fix the sessionId that will be assigned to the session with this parameter.
        :param media_mode: ROUTED (default) or RELAYED
        :return: The created OpenViduSession instance.
        """
        with self._lock:
            # Prepare parameters
            if media_mode not in ['ROUTED', 'RELAYED', None]:
                raise ValueError(f"media_mode must be any of ROUTED or RELAYED, not {media_mode}")

            parameters = {"mediaMode": media_mode, "customSessionId": custom_session_id}
            parameters = {k: v for k, v in parameters.items() if v is not None}

            # send request
            r = self._session.post('api/sessions', json=parameters)

            if r.status_code == 409:
                raise OpenViduSessionExistsError()
            elif r.status_code == 400:
                raise ValueError()

            r.raise_for_status()

            self.fetch()  # because the POST does not return the proper data object...
            return self.get_session(r.json()['id'])

    @property
    def sessions(self) -> List[OpenViduSession]:
        """
        Get a list of currently active sessions to the server.

        :return: A list of OpenViduSession objects.
        """
        with self._lock:
            return [
                sess for sess in self._openvidu_sessions.values() if sess.is_valid
            ]  # yeah... the fetch() hell just begun

    @property
    def session_count(self) -> int:
        """
        Get the number of active sessions on the server.

        :return: The number of active sessions.
        """
        with self._lock:
            return len(self.sessions)

    def get_config(self) -> dict:
        """
        Get OpenVidu active configuration.

        Unlike session related calls. This call does not require prior calling of the fetch() method.
        Using this function will always result an API call to the backend.

        https://docs.openvidu.io/en/2.12.0/reference-docs/REST-API/#get-config

        :return: The exact response from the server as a dict.
        """
        r = self._session.get('config')
        r.raise_for_status()

        return r.json()
