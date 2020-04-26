#!/usr/bin/env python3

"""Tests for OpenViduSession object"""

import pytest
from datetime import datetime
from pyopenvidu import OpenVidu, OpenViduError, OpenViduSessionDoesNotExistsError, OpenViduConnectionDoesNotExistsError
from urllib.parse import urljoin
from copy import deepcopy

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


#
# Token generation
#

def test_session_token(session_instance, requests_mock):
    token_response = {
        "id": "wss://localhost:4443?sessionId=zfgmthb8jl9uellk&token=lnlrtnkwm4v8l7uc&role=PUBLISHER&turnUsername=FYYNRC&turnCredential=yfxxs3",
        "session": "zfgmthb8jl9uellk", "role": "PUBLISHER", "data": "User Data",
        "token": "wss://localhost:4443?sessionId=zfgmthb8jl9uellk&token=lnlrtnkwm4v8l7uc&role=PUBLISHER&turnUsername=FYYNRC&turnCredential=yfxxs3",
        "kurentoOptions": {"videoMaxSendBandwidth": 700, "allowedFilters": ["GStreamerFilter", "ZBarFilter"]}}

    adapter = requests_mock.post(urljoin(URL_BASE, 'api/tokens'), json=token_response)

    token = session_instance.generate_token()

    assert token == token_response['token']
    assert adapter.last_request.json() == {'role': 'PUBLISHER', 'session': 'TestSession'}


def test_session_token_extra(session_instance, requests_mock):
    token_response = {
        "id": "wss://localhost:4443?sessionId=zfgmthb8jl9uellk&token=lnlrtnkwm4v8l7uc&role=PUBLISHER&turnUsername=FYYNRC&turnCredential=yfxxs3",
        "session": "zfgmthb8jl9uellk", "role": "PUBLISHER", "data": "User Data",
        "token": "wss://localhost:4443?sessionId=zfgmthb8jl9uellk&token=lnlrtnkwm4v8l7uc&role=PUBLISHER&turnUsername=FYYNRC&turnCredential=yfxxs3",
        "kurentoOptions": {"videoMaxSendBandwidth": 700, "allowedFilters": ["GStreamerFilter", "ZBarFilter"]}}

    adapter = requests_mock.post(urljoin(URL_BASE, 'api/tokens'), json=token_response)

    token = session_instance.generate_token(role='MODERATOR', data="meme machine", video_max_send_bandwidth=2500)

    assert token == token_response['token']
    assert adapter.last_request.json() == {
        'role': 'MODERATOR',
        'session': 'TestSession',
        'data': 'meme machine',
        'kurentoOptions': {'videoMaxSendBandwidth': 2500}
    }


def test_session_token_validation_error(session_instance):
    with pytest.raises(ValueError):
        session_instance.generate_token(role='abc')


def test_token_invalid_session_early(session_instance):
    session_instance._data = {}

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.generate_token()


def test_session_token_missing_session(session_instance, requests_mock):
    requests_mock.post(urljoin(URL_BASE, 'api/tokens'), json={}, status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.generate_token()


def test_session_token_serverside_validation_error(session_instance, requests_mock):
    requests_mock.post(urljoin(URL_BASE, 'api/tokens'), json={}, status_code=400)

    with pytest.raises(ValueError):
        session_instance.generate_token()


#
# Closing
#


def test_session_close(session_instance, requests_mock):
    adapter = requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession'), status_code=204)

    session_instance.close()

    assert adapter.called
    assert not session_instance.is_valid


def test_session_close_missing(session_instance, requests_mock):
    requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession'), status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.close()

    assert not session_instance.is_valid


#
# Connections
#

def test_connection_invalid_session_missing(session_instance):

    session_instance._data = {}

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        c = list(session_instance.connections)


def test_connection(session_instance):
    conn = session_instance.get_connection('vhdxz7abbfirh2lh')  # magic string

    assert conn.id == 'vhdxz7abbfirh2lh'


def test_missing_connection(session_instance):
    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        session_instance.get_connection('abc')



def test_connection_invalid_session_early(session_instance):

    session_instance._data = {}

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        conn = session_instance.get_connection('vhdxz7abbfirh2lh')


def test_connections(session_instance):
    conns = list(session_instance.connections)

    assert len(conns) == 3
    assert conns[0].id == 'vhdxz7abbfirh2lh'
    assert conns[1].id == 'maxawd3ysuj1rxvq'
    assert conns[2].id == 'maxawc4zsuj1rxva'


def test_connections_count(session_instance):
    assert session_instance.connection_count == 3

def test_connections_count_invalid_session_early(session_instance):
    session_instance._data = {}

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        a = session_instance.connection_count


#
# Signals
#

def test_signal_basic(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/signal'), status_code=200)

    session_instance.signal('MY_TYPE', "Hello world!")

    assert a.last_request.json() == {
        "session": SESSIONS['content'][0]['sessionId'],
        "type": "MY_TYPE",
        "data": "Hello world!"
    }


def test_signal_extra(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/signal'), status_code=200)
    connections = list(session_instance.connections)

    session_instance.signal('MY_TYPE', "Hello world!", connections)

    assert a.last_request.json() == {
        "session": SESSIONS['content'][0]['sessionId'],
        "type": "MY_TYPE",
        "data": "Hello world!",
        "to": [connection.id for connection in connections]
    }


def test_signal_value_error(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/signal'), status_code=400)

    with pytest.raises(ValueError):
        session_instance.signal('MY_TYPE', "Hello world!")


def test_signal_no_session(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/signal'), status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.signal('MY_TYPE', "Hello world!")

    assert a.called


def test_signal_early_no_session(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/signal'), status_code=404)
    b = requests_mock.get(urljoin(URL_BASE, 'api/sessions/TestSession'), json={}, status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.fetch()

    assert b.called

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.signal('MY_TYPE', "Hello world!")

    assert not a.called


def test_signal_no_connection(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/signal'), status_code=406)

    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        session_instance.signal('MY_TYPE', "Hello world!")


#
# IPCAM
#

def test_publish_simple(session_instance, requests_mock):
    new_connection_data = {
        "connectionId": "ipc_IPCAM_rtsp_A8MJ_91_191_213_49_555_live_mpeg4_sdp",
        "createdAt": 1582121476380,
        "location": "unknown",
        "platform": "IPCAM",
        "role": "PUBLISHER",
        "serverData": "",
        "publishers": [
            {
                "createdAt": 1582121476439,
                "streamId": "str_IPC_XC1W_ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp",
                "rtspUri": "rtsp://91.191.213.50:554/live_mpeg4.sdp",
                "mediaOptions": {
                    "hasAudio": True,
                    "audioActive": True,
                    "hasVideo": True,
                    "videoActive": True,
                    "typeOfVideo": "IPCAM",
                    "frameRate": None,
                    "videoDimensions": None,
                    "filter": {},
                    "adaptativeBitrate": True,
                    "onlyPlayWithSubscribers": True
                }
            }
        ],
        "subscribers": []
    }

    a = requests_mock.post(urljoin(URL_BASE, 'api/sessions/TestSession/connection'), json=new_connection_data)

    new_connection = session_instance.publish("rtsp://91.191.213.50:554/live_mpeg4.sdp")

    assert a.last_request.json() == {
        "type": "IPCAM",
        "rtspUri": "rtsp://91.191.213.50:554/live_mpeg4.sdp",
        "adaptativeBitrate": True,
        "onlyPlayWithSubscribers": True,
        "data": ''
    }

    assert a.called

    assert new_connection.id == 'ipc_IPCAM_rtsp_A8MJ_91_191_213_49_555_live_mpeg4_sdp'
    assert new_connection.role == 'PUBLISHER'
    assert new_connection.client_data is None
    assert new_connection.token is None
    assert new_connection.server_data == ''
    assert new_connection.created_at == datetime.utcfromtimestamp(1582121476380 / 1000.0)
    assert new_connection.publishers[0].created_at == datetime.utcfromtimestamp(1582121476439 / 1000.0)
    assert new_connection.publishers[0].stream_id == 'str_IPC_XC1W_ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp'
    assert new_connection.publishers[0].rtsp_uri == 'rtsp://91.191.213.50:554/live_mpeg4.sdp'
    assert new_connection.publishers[0].session_id == 'TestSession'
    assert new_connection.publishers[0].media_options == new_connection_data['publishers'][0]['mediaOptions']


def test_publish_extra(session_instance, requests_mock):
    new_connection_data = {
        "connectionId": "ipc_IPCAM_rtsp_A8MJ_91_191_213_49_555_live_mpeg4_sdp",
        "createdAt": 1582121476380,
        "location": "unknown",
        "platform": "IPCAM",
        "role": "PUBLISHER",
        "serverData": "TEST_DATA",
        "publishers": [
            {
                "createdAt": 1582121476439,
                "streamId": "str_IPC_XC1W_ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp",
                "rtspUri": "rtsp://91.191.213.50:554/live_mpeg4.sdp",
                "mediaOptions": {
                    "hasAudio": True,
                    "audioActive": True,
                    "hasVideo": True,
                    "videoActive": True,
                    "typeOfVideo": "IPCAM",
                    "frameRate": None,
                    "videoDimensions": None,
                    "filter": {},
                    "adaptativeBitrate": False,
                    "onlyPlayWithSubscribers": True
                }
            }
        ],
        "subscribers": []
    }

    a = requests_mock.post(urljoin(URL_BASE, 'api/sessions/TestSession/connection'), json=new_connection_data)

    new_connection = session_instance.publish("rtsp://91.191.213.50:554/live_mpeg4.sdp", "TEST_DATA",
                                              adaptive_bitrate=False)

    assert a.last_request.json() == {
        "type": "IPCAM",
        "rtspUri": "rtsp://91.191.213.50:554/live_mpeg4.sdp",
        "adaptativeBitrate": False,
        "onlyPlayWithSubscribers": True,
        "data": 'TEST_DATA'
    }

    assert a.called

    assert new_connection.id == 'ipc_IPCAM_rtsp_A8MJ_91_191_213_49_555_live_mpeg4_sdp'
    assert new_connection.role == 'PUBLISHER'
    assert new_connection.client_data is None
    assert new_connection.token is None
    assert new_connection.server_data == 'TEST_DATA'
    assert new_connection.created_at == datetime.utcfromtimestamp(1582121476380 / 1000.0)
    assert new_connection.publishers[0].created_at == datetime.utcfromtimestamp(1582121476439 / 1000.0)
    assert new_connection.publishers[0].stream_id == 'str_IPC_XC1W_ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp'
    assert new_connection.publishers[0].rtsp_uri == 'rtsp://91.191.213.50:554/live_mpeg4.sdp'
    assert new_connection.publishers[0].session_id == 'TestSession'
    assert new_connection.publishers[0].media_options == new_connection_data['publishers'][0]['mediaOptions']


def test_publish_invalid_session_fail_early(session_instance, requests_mock):
    session_instance._data = {}

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.publish("rtsp://91.191.213.50:554/live_mpeg4.sdp")


def test_publish_invalid_session(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/sessions/TestSession/connection'), json={}, status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.publish("rtsp://91.191.213.50:554/live_mpeg4.sdp")

    assert a.called


def test_publish_value_error(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/sessions/TestSession/connection'), json={}, status_code=400)

    with pytest.raises(ValueError):
        session_instance.publish("rtsp://91.191.213.50:554/live_mpeg4.sdp")

    assert a.called


def test_publish_server_error(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/sessions/TestSession/connection'), json={}, status_code=500)

    with pytest.raises(OpenViduError):
        session_instance.publish("rtsp://91.191.213.50:554/live_mpeg4.sdp")

    assert a.called


#
# Fetching
#

def test_fetching_nothing_happened(session_instance):
    is_changed = session_instance.fetch()

    assert not is_changed


def test_fetching_session_became_invalid(session_instance, requests_mock):
    requests_mock.get(urljoin(URL_BASE, 'api/sessions/TestSession'), json={}, status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.fetch()

    assert not session_instance.is_valid


def test_fetching_changed(session_instance, requests_mock):
    original = deepcopy(SESSIONS['content'][0])
    original['connections']['numberOfElements'] = 4
    original['connections']['content'].append({
        "connectionId": "vhdxz7abbfirh3lh", "createdAt": 1538482606412, "location": "",
        "platform": "Chrome 69.0.3497.100 on Linux 64-bit",
        "token": "wss://localhost:4443?sessionId=TestSession&token=2ezkertrimk6nttk&role=PUBLISHER&turnUsername=H0EQLL&turnCredential=kjh48u",
        "role": "PUBLISHER", "serverData": "", "clientData": "TestClient1", "publishers":
            [
                {"createdAt": 1538482606976, "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU",
                 "mediaOptions": {"hasAudio": True, "audioActive": True, "hasVideo": True, "videoActive": True,
                                  "typeOfVideo": "CAMERA", "frameRate": 30,
                                  "videoDimensions": "{\"width\":640,\"height\":480}", "filter": {}}}
            ],
        "subscribers": []
    })

    a = requests_mock.get(urljoin(URL_BASE, 'api/sessions/TestSession'), json=original)

    is_changed = session_instance.fetch()

    assert session_instance.connection_count == 4

    assert list(session_instance.connections)[3].id == 'vhdxz7abbfirh3lh'

    assert is_changed
    assert a.called


def test_fetching_changed_fetch_by_parent(openvidu_instance, session_instance, requests_mock):
    original = deepcopy(SESSIONS)
    original['content'][0]['connections']['numberOfElements'] = 4
    original['content'][0]['connections']['content'].append({
        "connectionId": "vhdxz7abbfirh3lh", "createdAt": 1538482606412, "location": "",
        "platform": "Chrome 69.0.3497.100 on Linux 64-bit",
        "token": "wss://localhost:4443?sessionId=TestSession&token=2ezkertrimk6nttk&role=PUBLISHER&turnUsername=H0EQLL&turnCredential=kjh48u",
        "role": "PUBLISHER", "serverData": "", "clientData": "TestClient1", "publishers":
            [
                {"createdAt": 1538482606976, "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU",
                 "mediaOptions": {"hasAudio": True, "audioActive": True, "hasVideo": True, "videoActive": True,
                                  "typeOfVideo": "CAMERA", "frameRate": 30,
                                  "videoDimensions": "{\"width\":640,\"height\":480}", "filter": {}}}
            ],
        "subscribers": []
    })

    a = requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=original)

    is_changed = openvidu_instance.fetch()

    assert session_instance.connection_count == 4

    assert list(session_instance.connections)[3].id == 'vhdxz7abbfirh3lh'

    assert is_changed
    assert a.called


#
# Properties
#

def test_session_id(session_instance):
    assert session_instance.id == 'TestSession'


def test_session_is_valid_true(session_instance):
    assert session_instance.is_valid


def test_other_properties(session_instance):
    assert session_instance.is_being_recorded == SESSIONS['content'][0]['recording']
    assert session_instance.media_mode == SESSIONS['content'][0]['mediaMode']
    assert session_instance.created_at == datetime.utcfromtimestamp(SESSIONS['content'][0]['createdAt'] / 1000.0)
