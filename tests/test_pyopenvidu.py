#!/usr/bin/env python3

"""Tests for OpenVidu object"""

import pytest
from pyopenvidu import OpenVidu, OpenViduSessionDoesNotExistsError
from urllib.parse import urljoin

URL_BASE = 'http://test.openvidu.io:4443/'
SECRET = 'MY_SECRET'


@pytest.fixture
def openvidu_instance():
    yield OpenVidu(URL_BASE, SECRET)


def test_config(openvidu_instance, requests_mock):
    original = {"version": "2.9.0", "openviduPublicurl": URL_BASE, "openviduCdr": False,
                "maxRecvBandwidth": 1000, "minRecvBandwidth": 300, "maxSendBandwidth": 1000, "minSendBandwidth": 300,
                "openviduRecording": True, "openviduRecordingVersion": "2.8.0",
                "openviduRecordingPath": "/opt/openvidu/recordings/", "openviduRecordingPublicAccess": True,
                "openviduRecordingNotification": "publisher_moderator",
                "openviduRecordingCustomLayout": "/opt/openvidu/custom-layout/",
                "openviduRecordingAutostopTimeout": 120, "openviduWebhook": True,
                "openviduWebhookEndpoint": "http://localhost:7777/webhook/",
                "openviduWebhookHeaders": ["Authorization: Basic YWJjZDphYmNk"],
                "openviduWebhookEvents": ["recordingStatusChanged"]}

    requests_mock.get(urljoin(URL_BASE, 'config'), json=original)

    a = openvidu_instance.get_config()

    assert a == original


def test_sessions_raw(openvidu_instance, requests_mock):
    original = {"numberOfElements": 1, "content": [
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
                                        "publisher": "vhdxz7abbfirh2lh"}]}]}, "recording": False}]}

    requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=original)

    a = openvidu_instance.get_sessions_info()

    assert a == original


def test_sessions(openvidu_instance, requests_mock):
    original = {"numberOfElements": 2, "content": [
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

    requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=original)

    sessions = list(openvidu_instance.get_sessions())

    assert len(sessions) == 2
    assert sessions[0].id == "TestSession"
    assert sessions[1].id == "TestSession2"


def test_session_count(openvidu_instance, requests_mock):
    original = {"numberOfElements": 2, "content": [
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

    requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=original)

    assert openvidu_instance.get_session_count() == 2


def test_no_sessions(openvidu_instance, requests_mock):
    original = {"numberOfElements": 0, "content": []}

    requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=original)

    sessions = list(openvidu_instance.get_sessions())

    assert len(sessions) == 0


def test_no_sessions_session_count(openvidu_instance, requests_mock):
    original = {"numberOfElements": 0, "content": []}

    requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=original)

    assert openvidu_instance.get_session_count() == 0


def test_session_raw(openvidu_instance, requests_mock):
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

    a = openvidu_instance.get_session_info('TestSession')

    assert a == original


def test_session_missing_session_info(openvidu_instance, requests_mock):
    requests_mock.get(urljoin(URL_BASE, 'api/sessions/TestSession'), json={}, status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        openvidu_instance.get_session_info('TestSession')


def test_session_missing_session(openvidu_instance, requests_mock):
    requests_mock.get(urljoin(URL_BASE, 'api/sessions/TestSession'), json={}, status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        openvidu_instance.get_session('TestSession')
