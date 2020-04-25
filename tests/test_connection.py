#!/usr/bin/env python3

"""Tests for OpenViduConnection object"""

import pytest
from pyopenvidu import OpenVidu, OpenViduSessionDoesNotExistsError, OpenViduConnectionDoesNotExistsError
from urllib.parse import urljoin
from datetime import datetime

URL_BASE = 'http://test.openvidu.io:4443/'
SESSIONS = {"numberOfElements": 2, "content": [
    {"sessionId": "TestSession", "createdAt": 1538482606338, "mediaMode": "ROUTED", "recordingMode": "MANUAL",
     "defaultOutputMode": "COMPOSED", "defaultRecordingLayout": "BEST_FIT", "customSessionId": "TestSession",
     "connections": {"numberOfElements": 3, "content": [
         {"connectionId": "vhdxz7abbfirh2lh", "createdAt": 1538482606412, "location": "",
          "platform": "Chrome 69.0.3497.100 on Linux 64-bit",
          "token": "wss://localhost:4443?sessionId=TestSession&token=2ezkertrimk6nttk&role=PUBLISHER&turnUsername=H0EQLL&turnCredential=kjh48u",
          "role": "PUBLISHER", "serverData": "", "clientData": "TestClient1", "publishers": [
             {"createdAt": 1538482606976, "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU",
              "mediaOptions": {"hasAudio": True, "audioActive": True, "hasVideo": True, "videoActive": True,
                               "typeOfVideo": "CAMERA", "frameRate": 30,
                               "videoDimensions": "{\"width\":640,\"height\":480}", "filter": {}}}],
          "subscribers": []},
         {"connectionId": "maxawd3ysuj1rxvq", "createdAt": 1538482607659, "location": "",
          "platform": "Chrome 69.0.3497.100 on Linux 64-bit",
          "token": "wss://localhost:4443?sessionId=TestSession&token=ovj1b4ysuqmcirti&role=PUBLISHER&turnUsername=INOAHN&turnCredential=oujrqd",
          "role": "PUBLISHER", "serverData": "", "clientData": "TestClient2", "publishers": [],
          "subscribers": [
              {"createdAt": 1538482607799, "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU"
               }
          ]},
         {"connectionId": "maxawc4zsuj1rxva", "createdAt": 1538482607659, "location": "",
          "platform": "Chrome 69.0.3497.100 on Linux 64-bit",
          "token": "wss://localhost:4443?sessionId=TestSession&token=ovj1b4ysuqmcirti&role=PUBLISHER&turnUsername=INOAHN&turnCredential=oujrqd",
          "role": "PUBLISHER", "publishers": [],
          "subscribers": [
              {"createdAt": 1538482607799, "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU"
               }
          ]},
     ]}, "recording": False},
    {"sessionId": "TestSession2", "createdAt": 1538482606338, "mediaMode": "ROUTED", "recordingMode": "MANUAL",
     "defaultOutputMode": "COMPOSED", "defaultRecordingLayout": "BEST_FIT", "customSessionId": "TestSession",
     "connections": {"numberOfElements": 3, "content": [
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
                                   {"createdAt": 1538482607799, "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU"}]},
         {"connectionId": "ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp", "createdAt": 1582121476379,
          "location": "unknown", "platform": "IPCAM", "role": "PUBLISHER", "serverData": "MY_IP_CAMERA", "publishers": [
             {"createdAt": 1582121476439,
              "streamId": "str_IPC_XC1W_ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp",
              "rtspUri": "rtsp://91.191.213.49:554/live_mpeg4.sdp",
              "mediaOptions": {"hasAudio": True, "audioActive": True, "hasVideo": True, "videoActive": True,
                               "typeOfVideo": "IPCAM", "frameRate": None, "videoDimensions": None, "filter": {},
                               "adaptativeBitrate": True, "onlyPlayWithSubscribers": True}}], "subscribers": []}

     ]},
     "recording": False}
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


#
# Disconnection
#

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


#
# Signals
#

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

    assert a.called


def test_signal_no_connection(connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/signal'), status_code=406)

    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        connection_instance.signal('MY_TYPE', "Hello world!")


#
# Unpublish
#

def test_force_unpublish_all(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=204)

    connection_instance.force_unpublish_all_streams()

    assert a.called


#
# Properties
#

def test_properties(connection_instance):
    assert connection_instance.session_id == SESSIONS['content'][0]['sessionId']
    assert connection_instance.id == SESSIONS['content'][0]['connections']['content'][0]['connectionId']

    assert connection_instance.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][0]['connections']['content'][0]['createdAt'] / 1000.0
    )

    assert connection_instance.token == SESSIONS['content'][0]['connections']['content'][0]['token']
    assert connection_instance.client_data == SESSIONS['content'][0]['connections']['content'][0]['clientData']
    assert connection_instance.server_data == SESSIONS['content'][0]['connections']['content'][0]['serverData']
    assert connection_instance.platform == SESSIONS['content'][0]['connections']['content'][0]['platform']
    assert connection_instance.role == SESSIONS['content'][0]['connections']['content'][0]['role']

    assert len(connection_instance.publishers) == len(SESSIONS['content'][0]['connections']['content'][0]['publishers'])


def test_properties_none_fields(session_instance):
    connection_instance = session_instance.get_connection('maxawc4zsuj1rxva')

    assert connection_instance.session_id == SESSIONS['content'][0]['sessionId']
    assert connection_instance.id == SESSIONS['content'][0]['connections']['content'][2]['connectionId']

    assert connection_instance.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][0]['connections']['content'][2]['createdAt'] / 1000.0
    )

    assert connection_instance.token == SESSIONS['content'][0]['connections']['content'][2]['token']
    assert connection_instance.client_data is None
    assert connection_instance.server_data is None
    assert connection_instance.platform == SESSIONS['content'][0]['connections']['content'][2]['platform']
    assert connection_instance.role == SESSIONS['content'][0]['connections']['content'][2]['role']

    assert len(connection_instance.publishers) == len(SESSIONS['content'][0]['connections']['content'][2]['publishers'])


def test_properties_ipcam_fields(openvidu_instance):
    session_instance = openvidu_instance.get_session('TestSession2')
    connection_instance = session_instance.get_connection('ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp')

    assert connection_instance.session_id == SESSIONS['content'][1]['sessionId']
    assert connection_instance.id == SESSIONS['content'][1]['connections']['content'][2]['connectionId']

    assert connection_instance.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][1]['connections']['content'][2]['createdAt'] / 1000.0
    )

    assert connection_instance.token is None
    assert connection_instance.client_data is None
    assert connection_instance.server_data == SESSIONS['content'][1]['connections']['content'][2]['serverData']
    assert connection_instance.platform == SESSIONS['content'][1]['connections']['content'][2]['platform']
    assert connection_instance.role == SESSIONS['content'][1]['connections']['content'][2]['role']

    assert len(connection_instance.publishers) == len(SESSIONS['content'][1]['connections']['content'][2]['publishers'])
