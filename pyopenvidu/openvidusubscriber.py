"""OpenViduSubscriber class."""
from requests_toolbelt.sessions import BaseUrlSession
from dataclasses import dataclass
from datetime import datetime


# Notice: Frozen should be changed to True in later versions of Python3 where a nice method for custom initializer is implemented
@dataclass(frozen=False, init=False)
class OpenViduSubscriber(object):
    session_id: str
    stream_id: str
    created_at: datetime
    publisher: str

    def __init__(self, session: BaseUrlSession, session_id: str, data: dict):
        self._session = session
        self.session_id = session_id
        self.stream_id = data['streamId']
        self.created_at = datetime.utcfromtimestamp(data['createdAt'] / 1000.0)
        self.publisher = data['publisher']

