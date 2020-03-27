#!/usr/bin/env python3

"""Tests for OpenViduSession object"""

import pytest
from pyopenvidu import OpenVidu, OpenViduSessionDoesNotExistsError
from urllib.parse import urljoin

URL_BASE = 'http://test.openvidu.io:4443/'
SECRET = 'MY_SECRET'


@pytest.fixture
def openvidu_instance():
    yield OpenVidu(URL_BASE, SECRET)


@pytest.fixture
def session_instance(requests_mock, openvidu_instance):
    original = {"sessionId": "TestSession", "createdAt": 1538482606338, "mediaMode": "ROUTED",
                "recordingMode": "MANUAL", "defaultOutputMode": "COMPOSED", "defaultRecordingLayout": "BEST_FIT",
                "customSessionId": "TestSession", "connections": {"numberOfElements": 2, "content": [
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

    requests_mock.get(urljoin(URL_BASE, 'api/sessions/TestSession'), json=original)

    yield openvidu_instance.get_session('TestSession')


def test_session_id(session_instance):
    assert session_instance.id == 'TestSession'


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


def test_session_token_value_error(session_instance):
    with pytest.raises(ValueError):
        session_instance.generate_token(role='abc')


def test_session_token_missing_session(session_instance, requests_mock):
    requests_mock.post(urljoin(URL_BASE, 'api/tokens'), json={}, status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.generate_token()


def test_session_is_valid_no(session_instance, requests_mock):
    requests_mock.get(urljoin(URL_BASE, 'api/sessions/TestSession'), json={}, status_code=404)

    assert session_instance.is_valid() == False


def test_session_is_valid_yes(session_instance, requests_mock):
    assert session_instance.is_valid() == True


def test_session_close(session_instance, requests_mock):
    adapter = requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession'), status_code=204)

    session_instance.close()

    assert adapter.called


def test_session_close_missing(session_instance, requests_mock):
    requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession'), status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.close()


def test_session_info(session_instance, requests_mock):
    original = {"sessionId": "TestSession", "createdAt": 1538482606338, "mediaMode": "ROUTED",
                "recordingMode": "MANUAL", "defaultOutputMode": "COMPOSED", "defaultRecordingLayout": "BEST_FIT",
                "customSessionId": "TestSession", "connections": {"numberOfElements": 2, "content": [
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

    requests_mock.get(urljoin(URL_BASE, 'api/sessions/TestSession'), json=original)

    a = session_instance.get_info()

    assert a == original
