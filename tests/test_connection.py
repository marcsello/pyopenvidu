#!/usr/bin/env python3

"""Tests for OpenViduConnection object"""

import pytest
from pyopenvidu import OpenVidu, OpenViduSessionDoesNotExistsError, OpenViduConnectionDoesNotExistsError
from urllib.parse import urljoin

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


def test_disconnection(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession/connection/vhdxz7abbfirh2lh'), json={},
                             status_code=204)

    connection_instance.force_disconnect()

    assert a.called


def test_disconnection_failed_no_connection(connection_instance, requests_mock):
    requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession/connection/vhdxz7abbfirh2lh'), json={},
                         status_code=404)

    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        connection_instance.force_disconnect()


def test_disconnection_failed_no_session(connection_instance, requests_mock):
    requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession/connection/vhdxz7abbfirh2lh'), json={},
                         status_code=400)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        connection_instance.force_disconnect()


def test_signal(connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/signal'), status_code=200)

    connection_instance.signal('MY_TYPE', "Hello world!")

    assert a.last_request.json() == {
        "session": SESSIONS['content'][0]['sessionId'],
        "type": "MY_TYPE",
        "data": "Hello world!",
        "to": [SESSIONS['content'][0]['connections']['content'][0]['connectionId']]

    }


def test_signal_value_error(connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/signal'), status_code=400)

    with pytest.raises(ValueError):
        connection_instance.signal('MY_TYPE', "Hello world!")


def test_signal_no_session(connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/signal'), status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        connection_instance.signal('MY_TYPE', "Hello world!")

    assert a.called == True


def test_signal_no_connection(connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/signal'), status_code=406)

    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        connection_instance.signal('MY_TYPE', "Hello world!")


def test_force_unpublish_all(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=204)

    connection_instance.force_unpublish_all_streams()

    assert a.called
