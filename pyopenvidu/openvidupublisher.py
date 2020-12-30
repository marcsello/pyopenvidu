"""OpenViduPublisher class."""
from typing import Optional
from requests_toolbelt.sessions import BaseUrlSession
from dataclasses import dataclass
from datetime import datetime
from .exceptions import OpenViduSessionDoesNotExistsError, OpenViduStreamDoesNotExistsError, OpenViduStreamError


# Notice: Frozen should be changed to True in later versions of Python3 where a nice method for custom initializer is implemented
@dataclass(frozen=False, init=False)
class OpenViduPublisher(object):
    session_id: str
    stream_id: str
    created_at: datetime
    media_options: Optional[dict]

    def __init__(self, session: BaseUrlSession, session_id: str, data: dict):
        """
        This is meant for internal use, thus you should not call it.
        Use `OpenViduConnection.publishers` to get an instance of this class.
        """

        self._session = session
        self.session_id = session_id
        self.stream_id = data['streamId']
        self.created_at = datetime.utcfromtimestamp(data['createdAt'] / 1000.0)
        self.media_options = data.get('mediaOptions')

    def force_unpublish(self):
        """
        Forces some user to unpublish a Stream. OpenVidu Browser will trigger the proper events on the client-side (streamDestroyed) with reason set to "forceUnpublishByServer".
        After this call, the instace of the object, and the parent OpenViduConnection instance should be considered invalid.
        Remember to call fetch() after this call to fetch the current actual properties of the Session from OpenVidu Server!

        https://docs.openvidu.io/en/2.16.0/reference-docs/REST-API/#delete-openviduapisessionsltsession_idgtstreamltstream_idgt
        """
        r = self._session.delete(f"sessions/{self.session_id}/stream/{self.stream_id}")
        if r.status_code == 404:
            raise OpenViduStreamDoesNotExistsError()
        if r.status_code == 400:
            raise OpenViduSessionDoesNotExistsError()
        if r.status_code == 405:
            raise OpenViduStreamError("You cannot directly delete the stream of an IPCAM participant.")

        r.raise_for_status()
