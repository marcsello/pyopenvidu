#!/usr/bin/env python3

"""Tests for OpenVidu object"""

import pytest
import requests.exceptions
from pyopenvidu import OpenVidu, OpenViduSessionDoesNotExistsError, OpenViduSessionExistsError
from urllib.parse import urljoin
from copy import deepcopy
from .fixtures import URL_BASE, SESSIONS, SECRET


@pytest.fixture
def no_fetch_openvidu_instance():
    yield OpenVidu(URL_BASE, SECRET, initial_fetch=False)


#
# Getting config
#

def test_get_config(openvidu_instance, requests_mock):
    original = {
        "VERSION": "2.16.0",
        "DOMAIN_OR_PUBLIC_IP": "my.openvidu.ip",
        "HTTPS_PORT": 443,
        "OPENVIDU_PUBLICURL": "https://my.openvidu.ip",
        "OPENVIDU_CDR": False,
        "OPENVIDU_STREAMS_VIDEO_MAX_RECV_BANDWIDTH": 1000,
        "OPENVIDU_STREAMS_VIDEO_MIN_RECV_BANDWIDTH": 300,
        "OPENVIDU_STREAMS_VIDEO_MAX_SEND_BANDWIDTH": 1000,
        "OPENVIDU_STREAMS_VIDEO_MIN_SEND_BANDWIDTH": 300,
        "OPENVIDU_SESSIONS_GARBAGE_INTERVAL": 900,
        "OPENVIDU_SESSIONS_GARBAGE_THRESHOLD": 3600,
        "OPENVIDU_RECORDING": True,
        "OPENVIDU_RECORDING_VERSION": "2.16.0",
        "OPENVIDU_RECORDING_PATH": "/opt/openvidu/recordings/",
        "OPENVIDU_RECORDING_PUBLIC_ACCESS": False,
        "OPENVIDU_RECORDING_NOTIFICATION": "moderator",
        "OPENVIDU_RECORDING_CUSTOM_LAYOUT": "/opt/openvidu/custom-layout/",
        "OPENVIDU_RECORDING_AUTOSTOP_TIMEOUT": 60,
        "OPENVIDU_WEBHOOK": True,
        "OPENVIDU_WEBHOOK_ENDPOINT": "http://my.webhook.endpoint:7777/webhook",
        "OPENVIDU_WEBHOOK_HEADERS": [],
        "OPENVIDU_WEBHOOK_EVENTS": [
            "sessionCreated",
            "sessionDestroyed",
            "recordingStatusChanged"
        ]
    }

    a = requests_mock.get(urljoin(URL_BASE, 'config'), json=original)

    recieved_cfg = openvidu_instance.get_config()

    assert a.called_once
    assert recieved_cfg == original


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
    new_session = {
        "id": "TestSession3",
        "object": "session",
        "createdAt": 1538481996019,
        "mediaMode": "ROUTED",
        "recordingMode": "MANUAL",
        "defaultOutputMode": "COMPOSED",
        "defaultRecordingLayout": "CUSTOM",
        "defaultCustomLayout": "",
        "customSessionId": "TestSession3",
        "connections": {
            "numberOfElements": 0,
            "content": []
        },
        "recording": False
    }

    a = requests_mock.post(urljoin(URL_BASE, 'sessions'), json=new_session)

    NEW_SESSIONS = deepcopy(SESSIONS)
    NEW_SESSIONS['content'].append(new_session)

    NEW_SESSIONS['numberOfElements'] = len(NEW_SESSIONS['content'])

    b = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=NEW_SESSIONS)

    session = openvidu_instance.create_session()

    assert session.id == "TestSession3"
    assert a.called_once
    assert not b.called  # A subsequent fetch should not be called (since 2.16.0)

    assert a.last_request.json() == {}


def test_create_session_extra(openvidu_instance, requests_mock):
    new_session = {
        "id": "DerpyIsBestPony",
        "object": "session",
        "createdAt": 1538481996019,
        "mediaMode": "RELAYED",
        "recordingMode": "MANUAL",
        "defaultOutputMode": "COMPOSED",
        "defaultRecordingLayout": "CUSTOM",
        "defaultCustomLayout": "",
        "customSessionId": "DerpyIsBestPony",
        "connections": {
            "numberOfElements": 0,
            "content": []
        },
        "recording": False
    }

    a = requests_mock.post(urljoin(URL_BASE, 'sessions'), json=new_session)

    NEW_SESSIONS = deepcopy(SESSIONS)
    NEW_SESSIONS['content'].append(new_session)

    NEW_SESSIONS['numberOfElements'] = len(NEW_SESSIONS['content'])

    b = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=NEW_SESSIONS)

    session = openvidu_instance.create_session('DerpyIsBestPony', 'RELAYED')

    assert session.id == "DerpyIsBestPony"
    assert a.called_once
    assert not b.called  # A subsequent fetch should not be called (since 2.16.0)

    assert a.last_request.json() == {"mediaMode": 'RELAYED', "customSessionId": 'DerpyIsBestPony'}


def test_create_session_conflict(openvidu_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'sessions'), json={}, status_code=409)

    with pytest.raises(OpenViduSessionExistsError):
        openvidu_instance.create_session('TestSession')

    assert a.called_once


def test_create_session_bad_parameters(openvidu_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'sessions'), json={}, status_code=400)

    with pytest.raises(ValueError):
        openvidu_instance.create_session()

    assert a.called_once


def test_create_session_validation_error(openvidu_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'sessions'), json={}, status_code=400)

    with pytest.raises(ValueError):
        openvidu_instance.create_session(media_mode="asd")

    assert not a.called


def test_no_sessions(openvidu_instance, requests_mock):
    NEW_SESSIONS = {"numberOfElements": 0, "content": []}

    a = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=NEW_SESSIONS)

    is_changed = openvidu_instance.fetch()
    sessions = openvidu_instance.sessions

    assert a.called_once
    assert is_changed
    assert len(sessions) == 0


def test_no_sessions_session_count(openvidu_instance, requests_mock):
    NEW_SESSIONS = {"numberOfElements": 0, "content": []}

    a = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=NEW_SESSIONS)

    is_changed = openvidu_instance.fetch()

    assert a.called_once
    assert is_changed
    assert openvidu_instance.session_count == 0


def test_get_missing_session(openvidu_instance):
    with pytest.raises(OpenViduSessionDoesNotExistsError):
        openvidu_instance.get_session('Nonexistent')


#
# Fetching
#

def test_fetching_nothing_happened(openvidu_instance):
    is_changed = openvidu_instance.fetch()

    assert not is_changed


def test_fetching_deleted(openvidu_instance, requests_mock):
    session_before_delete = openvidu_instance.get_session('TestSession')

    NEW_SESSIONS = {"numberOfElements": 0, "content": []}
    a = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=NEW_SESSIONS)
    b = requests_mock.get(urljoin(URL_BASE, 'sessions/TestSession'), status_code=404)

    is_changed = openvidu_instance.fetch()
    assert a.called_once

    assert is_changed

    # The session should still report valid state, because it did not get fetched
    assert session_before_delete.is_valid

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        # the api returns 404
        session_before_delete.fetch()

    assert b.called_once
    # Since fetch called, this session shouldn't be valid anymore
    assert not session_before_delete.is_valid


def test_access_after_close_without_fetch(openvidu_instance, requests_mock):
    session_to_close = openvidu_instance.get_session('TestSession')
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession'), status_code=204)

    session_to_close.close()

    assert a.called_once

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        openvidu_instance.get_session('TestSession')


def test_inlist_after_close_without_fetch(openvidu_instance, requests_mock):
    session_to_close = openvidu_instance.get_session('TestSession')
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession'), status_code=204)

    session_to_close.close()

    assert a.called_once

    assert len(openvidu_instance.sessions) == 1
    assert openvidu_instance.session_count == 1


def test_fetching_changed(openvidu_instance, requests_mock):
    session_before_change = openvidu_instance.get_session('TestSession')

    assert session_before_change.connection_count == SESSIONS['content'][0]['connections']['numberOfElements']

    NEW_SESSIONS = deepcopy(SESSIONS)  # Deep copy
    new_connection = {
        "id": "con_Xnxg19tonh",
        "object": "connection",
        "type": "WEBRTC",
        "status": "pending",
        "sessionId": "ses_YnDaGYNcd7",
        "createdAt": 1538481999022,
        "activeAt": 1538481999843,
        "platform": "Chrome 85.0.4183.102 on Linux 64-bit",
        "token": "wss://localhost:4443?sessionId=TestSession&token=tok_AVe8o7iltWqtijyl&role=PUBLISHER&version=2.16.0&coturnIp=localhost&turnUsername=M2ALIY&turnCredential=7kfjy2",
        "serverData": "My Server Data",
        "clientData": "",
        "record": False,
        "role": "PUBLISHER",
        "kurentoOptions": {
            "videoMaxRecvBandwidth": 1000,
            "videoMinRecvBandwidth": 300,
            "videoMaxSendBandwidth": 1000,
            "videoMinSendBandwidth": 300,
            "allowedFilters": [
                "GStreamerFilter",
                "ZBarFilter"
            ]
        },
        "publishers": [

        ],
        "subscribers": [

        ]
    }

    NEW_SESSIONS['content'][0]['connections']['content'].append(new_connection)
    NEW_SESSIONS['content'][0]['connections']['numberOfElements'] = len(NEW_SESSIONS['content'][0]['connections']['content'])

    a = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=NEW_SESSIONS)

    is_changed = openvidu_instance.fetch()

    assert a.called_once
    assert is_changed

    # fetch() was not called on the session object, so it should not change
    assert session_before_change.connection_count == SESSIONS['content'][0]['connections']['numberOfElements']


def test_fetching_new(openvidu_instance, requests_mock):
    assert openvidu_instance.session_count == SESSIONS['numberOfElements']

    new_session = {
        "id": "TestSession3",
        "object": "session",
        "createdAt": 1538481996019,
        "mediaMode": "RELAYED",
        "recordingMode": "MANUAL",
        "defaultOutputMode": "COMPOSED",
        "defaultRecordingLayout": "CUSTOM",
        "defaultCustomLayout": "",
        "customSessionId": "TestSession3",
        "connections": {
            "numberOfElements": 0,
            "content": []
        },
        "recording": False
    }

    NEW_SESSIONS = deepcopy(SESSIONS)

    NEW_SESSIONS['content'].append(new_session)
    NEW_SESSIONS['numberOfElements'] = len(NEW_SESSIONS['content'])

    a = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=NEW_SESSIONS)

    is_changed = openvidu_instance.fetch()

    assert a.called_once
    assert openvidu_instance.session_count == NEW_SESSIONS['numberOfElements']
    assert openvidu_instance.get_session('TestSession3').id == 'TestSession3'
    assert is_changed


#
# Tests without initial fetch
#

def test_empty_with_no_fetch(requests_mock):
    a = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=SESSIONS)
    openvidu_instance = OpenVidu(URL_BASE, SECRET, initial_fetch=False)

    assert not a.called_once

    assert openvidu_instance.sessions == []
    assert openvidu_instance.session_count == 0


def test_proper_error_with_no_fetch(no_fetch_openvidu_instance):
    with pytest.raises(OpenViduSessionDoesNotExistsError):
        no_fetch_openvidu_instance.get_session("TestSession")


def test_new_session_proper_working_with_no_fetch(no_fetch_openvidu_instance, requests_mock):
    new_session = {
        "id": "TestSession3",
        "object": "session",
        "createdAt": 1538481996019,
        "mediaMode": "ROUTED",
        "recordingMode": "MANUAL",
        "defaultOutputMode": "COMPOSED",
        "defaultRecordingLayout": "CUSTOM",
        "defaultCustomLayout": "",
        "customSessionId": "TestSession3",
        "connections": {
            "numberOfElements": 0,
            "content": []
        },
        "recording": False
    }

    a = requests_mock.post(urljoin(URL_BASE, 'sessions'), json=new_session)

    NEW_SESSIONS = deepcopy(SESSIONS)
    NEW_SESSIONS['content'].append(new_session)

    NEW_SESSIONS['numberOfElements'] = len(NEW_SESSIONS['content'])

    b = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=NEW_SESSIONS)

    session = no_fetch_openvidu_instance.create_session()

    assert session.id == "TestSession3"
    assert a.called_once
    assert not b.called_once  # Nofetch (as of 2.16.0)

    assert a.last_request.json() == {}


def test_create_session_extra_proper_working_with_no_fetch(no_fetch_openvidu_instance, requests_mock):
    new_session = {
        "id": "DerpyIsBestPony",
        "object": "session",
        "createdAt": 1538481996019,
        "mediaMode": "RELAYED",
        "recordingMode": "MANUAL",
        "defaultOutputMode": "COMPOSED",
        "defaultRecordingLayout": "CUSTOM",
        "defaultCustomLayout": "",
        "customSessionId": "DerpyIsBestPony",
        "connections": {
            "numberOfElements": 0,
            "content": []
        },
        "recording": False
    }

    a = requests_mock.post(urljoin(URL_BASE, 'sessions'), json=new_session)

    NEW_SESSIONS = deepcopy(SESSIONS)
    NEW_SESSIONS['content'].append(new_session)

    NEW_SESSIONS['numberOfElements'] = len(NEW_SESSIONS['content'])

    b = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=NEW_SESSIONS)

    session = no_fetch_openvidu_instance.create_session('DerpyIsBestPony', 'RELAYED')

    assert session.id == "DerpyIsBestPony"
    assert a.called_once
    assert not b.called  # A subsequent fetch should not be called (since 2.16.0)

    assert a.last_request.json() == {"mediaMode": 'RELAYED', "customSessionId": 'DerpyIsBestPony'}



def test_create_session_conflict_proper_working_with_no_fetch(no_fetch_openvidu_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'sessions'), json={}, status_code=409)

    with pytest.raises(OpenViduSessionExistsError):
        no_fetch_openvidu_instance.create_session('TestSession')

    assert a.called_once


def test_create_session_bad_parameters_proper_working_with_no_fetch(no_fetch_openvidu_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'sessions'), json={}, status_code=400)

    with pytest.raises(ValueError):
        no_fetch_openvidu_instance.create_session()

    assert a.called_once


def test_create_session_validation_error_proper_working_with_no_fetch(no_fetch_openvidu_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'sessions'), json={}, status_code=400)

    with pytest.raises(ValueError):
        no_fetch_openvidu_instance.create_session(media_mode="asd")

    assert not a.called


def test_fetch_with_no_fetch(no_fetch_openvidu_instance, requests_mock):
    a = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=SESSIONS)
    is_changed = no_fetch_openvidu_instance.fetch()

    assert a.called_once
    assert is_changed == True

    sessions = no_fetch_openvidu_instance.sessions

    assert len(sessions) == 2
    assert sessions[0].id == "TestSession"
    assert sessions[1].id == "TestSession2"


def test_timeout(requests_mock):
    openvidu_instance = OpenVidu(URL_BASE, SECRET, initial_fetch=False, timeout=2)

    # This will always raise the exception, regardless if timeout is set or not
    a = requests_mock.get(urljoin(URL_BASE, 'sessions'), exc=requests.exceptions.ConnectTimeout)

    with pytest.raises(requests.exceptions.ConnectTimeout):
        openvidu_instance.fetch()

    assert a.called_once


def test_timeout2_int(mocker):
    # So we test if the value properly set
    openvidu_instance = OpenVidu(URL_BASE, SECRET, initial_fetch=False, timeout=2)

    mocker.patch.object(requests.Session, "request", autospec=True)

    openvidu_instance.fetch()

    args, kwargs = requests.Session.request.call_args

    assert kwargs['timeout'] == 2


def test_timeout2_tuple(mocker):
    # So we test if the value properly set
    openvidu_instance = OpenVidu(URL_BASE, SECRET, initial_fetch=False, timeout=(1, 2))

    mocker.patch.object(requests.Session, "request", autospec=True)

    openvidu_instance.fetch()

    args, kwargs = requests.Session.request.call_args

    assert kwargs['timeout'] == (1, 2)
