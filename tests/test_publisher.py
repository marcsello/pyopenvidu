#!/usr/bin/env python3

"""Tests for OpenViduConnection object"""

import pytest
from pyopenvidu import OpenVidu, OpenViduStreamDoesNotExistsError, OpenViduSessionDoesNotExistsError, \
    OpenViduStreamError
from urllib.parse import urljoin
from datetime import datetime

URL_BASE = 'http://test.openvidu.io:4443/'
SESSIONS = {"numberOfElements": 2, "content": [
    {"sessionId": "TestSession", "createdAt": 1538482606338, "mediaMode": "ROUTED", "recordingMode": "MANUAL",
     "defaultOutputMode": "COMPOSED", "defaultRecordingLayout": "BEST_FIT", "customSessionId": "TestSession",
     "connections": {"numberOfElements": 2, "content": [
         {"connectionId": "vhdxz7abbfirh2lh", "createdAt": 1538482606412, "location": "",
          "platform": "Chrome 69.0.3497.100 on Linux 64-bit",
          "token": "wss://localhost:4443?sessionId=TestSession&token=2ezkertrimk6nttk&role=PUBLISHER&turnUsername=H0EQLL&turnCredential=kjh48u",
          "role": "PUBLISHER", "serverData": "", "clientData": "TestClient1", "publishers": [
             {"createdAt": 1538482606976, "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU",
              "mediaOptions": {"hasAudio": True, "audioActive": True, "hasVideo": True, "videoActive": True,
                               "typeOfVideo": "CAMERA", "frameRate": 30,
                               "videoDimensions": "{\"width\":640,\"height\":480}", "filter": {}}}],
          "subscribers": []}, {"connectionId": "maxawd3ysuj1rxvq", "createdAt": 1538482607659, "location": "",
                               "platform": "Chrome 69.0.3497.100 on Linux 64-bit",
                               "token": "wss://localhost:4443?sessionId=TestSession&token=ovj1b4ysuqmcirti&role=PUBLISHER&turnUsername=INOAHN&turnCredential=oujrqd",
                               "role": "PUBLISHER", "serverData": "", "clientData": "TestClient2", "publishers": [],
                               "subscribers": [
                                   {"createdAt": 1538482607799, "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU",
                                    "publisher": "vhdxz7abbfirh2lh"}]}]}, "recording": False},
    {"sessionId": "TestSession2", "createdAt": 1538482606338, "mediaMode": "ROUTED", "recordingMode": "MANUAL",
     "defaultOutputMode": "COMPOSED", "defaultRecordingLayout": "BEST_FIT", "customSessionId": "TestSession",
     "connections": {"numberOfElements": 2, "content": [
         {"connectionId": "vhdxz7abbfirh2lh", "createdAt": 1538482606412, "location": "",
          "platform": "Chrome 69.0.3497.100 on Linux 64-bit",
          "token": "wss://localhost:4443?sessionId=TestSession&token=2ezkertrimk6nttk&role=PUBLISHER&turnUsername=H0EQLL&turnCredential=kjh48u",
          "role": "PUBLISHER", "serverData": "", "clientData": "TestClient1", "publishers": [
             {"createdAt": 1538482606976, "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU",
              "mediaOptions": {"hasAudio": True, "audioActive": True, "hasVideo": True, "videoActive": True,
                               "typeOfVideo": "CAMERA", "frameRate": 30,
                               "videoDimensions": "{\"width\":640,\"height\":480}", "filter": {}}}],
          "subscribers": []}, {"connectionId": "maxawd3ysuj1rxvq", "createdAt": 1538482607659, "location": "",
                               "platform": "Chrome 69.0.3497.100 on Linux 64-bit",
                               "token": "wss://localhost:4443?sessionId=TestSession&token=ovj1b4ysuqmcirti&role=PUBLISHER&turnUsername=INOAHN&turnCredential=oujrqd",
                               "role": "PUBLISHER", "serverData": "", "clientData": "TestClient2", "publishers": [],
                               "subscribers": [
                                   {"createdAt": 1538482607799, "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU",
                                    "publisher": "vhdxz7abbfirh2lh"}]}]}, "recording": False}
]}
SECRET = 'MY_SECRET'


@pytest.fixture
def openvidu_instance(requests_mock):
    requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=SESSIONS)
    requests_mock.get(urljoin(URL_BASE, 'api/sessions/TestSession'), json=SESSIONS['content'][0])
    requests_mock.get(urljoin(URL_BASE, 'api/sessions/TestSession2'), json=SESSIONS['content'][1])
    yield OpenVidu(URL_BASE, SECRET)


@pytest.fixture
def session_instance(openvidu_instance):
    yield openvidu_instance.get_session('TestSession')


@pytest.fixture
def connection_instance(session_instance):
    yield session_instance.get_connection('vhdxz7abbfirh2lh')


def test_unpublish(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=204)

    connection_instance.publishers[0].force_unpublish()

    assert a.called


def test_unpublish_no_publisher(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=404)

    with pytest.raises(OpenViduStreamDoesNotExistsError):
        connection_instance.publishers[0].force_unpublish()

    assert a.called


def test_unpublish_no_session(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=400)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        connection_instance.publishers[0].force_unpublish()

    assert a.called


def test_unpublish_ipcam(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=405)

    with pytest.raises(OpenViduStreamError):
        connection_instance.publishers[0].force_unpublish()

    assert a.called


def test_properties(connection_instance):
    p = connection_instance.publishers[0]

    assert p.session_id == SESSIONS['content'][0]['sessionId']
    assert p.stream_id == SESSIONS['content'][0]['connections']['content'][0]['publishers'][0]['streamId']

    assert p.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][0]['connections']['content'][0]['publishers'][0]['createdAt'] / 1000.0
    )

    assert p.media_options == SESSIONS['content'][0]['connections']['content'][0]['publishers'][0]['mediaOptions']
