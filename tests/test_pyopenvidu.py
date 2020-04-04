#!/usr/bin/env python3

"""Tests for OpenVidu object"""

import pytest
from pyopenvidu import OpenVidu, OpenViduSessionDoesNotExistsError, OpenViduSessionExistsError
from urllib.parse import urljoin
from copy import deepcopy

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
    yield OpenVidu(URL_BASE, SECRET)


#
# Getting config
#

def test_get_config(openvidu_instance, requests_mock):
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


#
# Sessions
#


def test_get_sessions(openvidu_instance):
    sessions = openvidu_instance.sessions

    assert len(sessions) == 2
    assert sessions[0].id == "TestSession"
    assert sessions[1].id == "TestSession2"


def test_session_count(openvidu_instance):
    assert openvidu_instance.session_count == 2


def test_create_session(openvidu_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/sessions'),
                           json={"id": "zfgmthb8jl9uellk", "createdAt": 1538481996019})

    NEW_SESSIONS = deepcopy(SESSIONS)
    NEW_SESSIONS['content'].append({"sessionId": "zfgmthb8jl9uellk",
                                    "createdAt": 1538481996019,
                                    "mediaMode": "ROUTED",
                                    "recordingMode": "MANUAL",
                                    "defaultOutputMode": "COMPOSED",
                                    "defaultRecordingLayout": "BEST_FIT",
                                    "customSessionId": "TestSession",
                                    "connections": {"numberOfElements": 0, "content": []},
                                    "recording": False})
    NEW_SESSIONS['numberOfElements'] = len(NEW_SESSIONS['content'])

    b = requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=NEW_SESSIONS)

    session = openvidu_instance.create_session()

    assert session.id == "zfgmthb8jl9uellk"
    assert a.called
    assert b.called

    assert a.last_request.json() == {}


def test_create_session_extra(openvidu_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/sessions'),
                           json={"id": "DerpyIsBestPony", "createdAt": 1538481996019})

    NEW_SESSIONS = deepcopy(SESSIONS)
    NEW_SESSIONS['content'].append({"sessionId": "DerpyIsBestPony",
                                    "createdAt": 1538481996019,
                                    "mediaMode": "RELAYED",
                                    "recordingMode": "MANUAL",
                                    "defaultOutputMode": "COMPOSED",
                                    "defaultRecordingLayout": "BEST_FIT",
                                    "customSessionId": "TestSession",
                                    "connections": {"numberOfElements": 0, "content": []},
                                    "recording": False})
    NEW_SESSIONS['numberOfElements'] = len(NEW_SESSIONS['content'])

    b = requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=NEW_SESSIONS)

    session = openvidu_instance.create_session('DerpyIsBestPony', 'RELAYED')

    assert session.id == "DerpyIsBestPony"
    assert a.called
    assert b.called

    assert a.last_request.json() == {"mediaMode": 'RELAYED', "customSessionId": 'DerpyIsBestPony'}


def test_create_session_conflict(openvidu_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/sessions'), json={}, status_code=409)

    with pytest.raises(OpenViduSessionExistsError):
        openvidu_instance.create_session('TestSession')

    assert a.called


def test_create_session_bad_parameters(openvidu_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/sessions'), json={}, status_code=400)

    with pytest.raises(ValueError):
        openvidu_instance.create_session()

    assert a.called


def test_create_session_validation_error(openvidu_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'api/sessions'), json={}, status_code=400)

    with pytest.raises(ValueError):
        openvidu_instance.create_session(media_mode="asd")

    assert not a.called


def test_no_sessions(openvidu_instance, requests_mock):
    original = {"numberOfElements": 0, "content": []}

    requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=original)

    is_changed = openvidu_instance.fetch()
    sessions = openvidu_instance.sessions

    assert is_changed
    assert len(sessions) == 0


def test_no_sessions_session_count(openvidu_instance, requests_mock):
    original = {"numberOfElements": 0, "content": []}

    requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=original)

    is_changed = openvidu_instance.fetch()

    assert is_changed
    assert openvidu_instance.session_count == 0


def test_get_missing_session(openvidu_instance):
    with pytest.raises(OpenViduSessionDoesNotExistsError):
        openvidu_instance.get_session('Nonexistent')


#
# Fetching
#


def test_fetching_deleted(openvidu_instance, requests_mock):
    session_before_delete = openvidu_instance.get_session('TestSession')

    original = {"numberOfElements": 0, "content": []}
    requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=original)

    is_changed = openvidu_instance.fetch()

    assert not session_before_delete.is_valid
    assert is_changed

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_before_delete.fetch()


def test_access_after_close_without_fetch(openvidu_instance, requests_mock):
    session_to_close = openvidu_instance.get_session('TestSession')
    a = requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession'), status_code=204)

    session_to_close.close()

    assert a.called

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        openvidu_instance.get_session('TestSession')


def test_inlist_after_close_without_fetch(openvidu_instance, requests_mock):
    session_to_close = openvidu_instance.get_session('TestSession')
    a = requests_mock.delete(urljoin(URL_BASE, 'api/sessions/TestSession'), status_code=204)

    session_to_close.close()

    assert a.called

    assert len(openvidu_instance.sessions) == 1
    assert openvidu_instance.session_count == 1


def test_fetching_changed(openvidu_instance, requests_mock):
    session_before_change = openvidu_instance.get_session('TestSession')

    assert session_before_change.connection_count == 2

    original = deepcopy(SESSIONS)  # Deep copy
    original['content'][0]['connections']['numberOfElements'] = 3
    original['content'][0]['connections']['content'].append(
        {"connectionId": "vhdxz7a3bfirh2lh", "createdAt": 1538482606412, "location": "",
         "platform": "Chrome 69.0.3497.100 on Linux 64-bit",
         "token": "wss://localhost:4443?sessionId=TestSession&token=2ezkertrimk6nttk&role=PUBLISHER&turnUsername=H0EQLL&turnCredential=kjh48u",
         "role": "PUBLISHER", "serverData": "", "clientData": "TestClient1", "publishers": [
            {"createdAt": 1538482606976, "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU",
             "mediaOptions": {"hasAudio": True, "audioActive": True, "hasVideo": True, "videoActive": True,
                              "typeOfVideo": "CAMERA", "frameRate": 30,
                              "videoDimensions": "{\"width\":640,\"height\":480}", "filter": {}}}],
         "subscribers": []})

    requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=original)

    is_changed = openvidu_instance.fetch()

    assert session_before_change.connection_count == 3
    assert is_changed


def test_fetching_new(openvidu_instance, requests_mock):
    assert openvidu_instance.session_count == 2

    original = deepcopy(SESSIONS)
    original['numberOfElements'] = 3
    original['content'].append(
        {"sessionId": "TestSession3", "createdAt": 1538482606338, "mediaMode": "ROUTED", "recordingMode": "MANUAL",
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
                                        "publisher": "vhdxz7abbfirh2lh"}]}]}, "recording": False})

    requests_mock.get(urljoin(URL_BASE, 'api/sessions'), json=original)

    is_changed = openvidu_instance.fetch()

    assert openvidu_instance.session_count == 3
    assert openvidu_instance.get_session('TestSession3').id == 'TestSession3'
    assert is_changed
