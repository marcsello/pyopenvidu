#!/usr/bin/env python3

"""Tests for OpenViduSession object"""

import pytest
from datetime import datetime
from pyopenvidu import OpenViduError, OpenViduSessionDoesNotExistsError, OpenViduConnectionDoesNotExistsError
from urllib.parse import urljoin
from copy import deepcopy
from .fixtures import URL_BASE, SESSIONS


#
# Token generation
#

def test_session_new_webrtc_connection(session_instance, requests_mock):
    new_connection_data = {
        "id": "con_Xnxg19tonh",
        "object": "connection",
        "type": "WEBRTC",
        "status": "active",
        "sessionId": "ses_YnDaGYNcd7",
        "createdAt": 1538481999022,
        "activeAt": 1538481999843,
        "platform": "Chrome 85.0.4183.102 on Linux 64-bit",
        "token": "wss://localhost:4443?sessionId=TestSession&token=tok_AVe8o7iltWqtijyl&role=PUBLISHER&version=2.16.0&coturnIp=localhost&turnUsername=M2ALIY&turnCredential=7kfjy2",
        "serverData": "",
        "clientData": "",
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
        "publishers": [],
        "subscribers": []
    }

    a = requests_mock.post(urljoin(URL_BASE, 'sessions/TestSession/connection'), json=new_connection_data)

    new_connection_instance = session_instance.create_webrtc_connection()

    assert new_connection_instance.token == new_connection_data['token']
    assert a.last_request.json() == {
        "type": "WEBRTC",
        "role": "PUBLISHER",
    }


def test_session_new_webrtc_connection_extra(session_instance, requests_mock):
    new_connection_data = {
        "id": "con_Xnxg19tonh",
        "object": "connection",
        "type": "WEBRTC",
        "status": "active",
        "sessionId": "ses_YnDaGYNcd7",
        "createdAt": 1538481999022,
        "activeAt": 1538481999843,
        "platform": "Chrome 85.0.4183.102 on Linux 64-bit",
        "token": "wss://localhost:4443?sessionId=TestSession&token=tok_AVe8o7iltWqtijyl&role=PUBLISHER&version=2.16.0&coturnIp=localhost&turnUsername=M2ALIY&turnCredential=7kfjy2",
        "serverData": "meme machine",
        "clientData": "My Client Data",
        "role": "MODERATOR",
        "kurentoOptions": {
            "videoMaxRecvBandwidth": 1000,
            "videoMinRecvBandwidth": 300,
            "videoMaxSendBandwidth": 2500,
            "videoMinSendBandwidth": 300,
            "allowedFilters": [
                "GStreamerFilter",
                "ZBarFilter"
            ]
        },
        "publishers": [],
        "subscribers": []
    }

    a = requests_mock.post(urljoin(URL_BASE, 'sessions/TestSession/connection'), json=new_connection_data)

    new_connection_instance = session_instance.create_webrtc_connection(role='MODERATOR', data="meme machine",
                                                                        video_max_send_bandwidth=2500)

    assert new_connection_instance.token == new_connection_data['token']
    assert a.last_request.json() == {
        'type': 'WEBRTC',
        'role': 'MODERATOR',
        'data': 'meme machine',
        'kurentoOptions': {'videoMaxSendBandwidth': 2500}
    }


def test_session_fetch_connection_invalid_type(session_instance, requests_mock):
    NEW_SESSIONS = deepcopy(SESSIONS)

    NEW_SESSIONS['content'][0]['connections']['content'][0]['type'] = "abc"

    a = requests_mock.get(urljoin(URL_BASE, 'sessions/TestSession'), json=NEW_SESSIONS['content'][0])

    with pytest.raises(RuntimeError):
        session_instance.fetch()

    assert a.called_once
    assert session_instance.is_valid  # This is undefined behaviour


def test_session_new_webrtc_connection_validation_error(session_instance):
    with pytest.raises(ValueError):
        session_instance.create_webrtc_connection(role='abc')

    assert session_instance.is_valid  # user error


def test_session_new_webrtc_connection_invalid_session_early(session_instance):
    session_instance.is_valid = False

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.create_webrtc_connection()


def test_session_new_webrtc_connection_missing_session(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'sessions/TestSession/connection'), json={}, status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.create_webrtc_connection()

    assert a.called_once
    assert not session_instance.is_valid


def test_session_new_webrtc_connection_serverside_validation_error(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'sessions/TestSession/connection'), json={}, status_code=400)

    with pytest.raises(ValueError):
        session_instance.create_webrtc_connection()

    assert a.called_once
    assert session_instance.is_valid  # user error it was


#
# Closing
#


def test_session_close(session_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession'), status_code=204)

    session_instance.close()

    assert a.called_once
    assert not session_instance.is_valid


def test_session_close_missing(session_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession'), status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.close()

    assert a.called_once
    assert not session_instance.is_valid


#
# Connections
#

def test_connection_invalid_session_missing(session_instance):
    session_instance.is_valid = False

    # No exception should be raised
    c = session_instance.connections


def test_connection(session_instance):
    conn = session_instance.get_connection('vhdxz7abbfirh2lh')  # magic string

    assert conn.id == 'vhdxz7abbfirh2lh'


def test_missing_connection(session_instance):
    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        session_instance.get_connection('abc')

    assert session_instance.is_valid  # meh


def test_connection_invalid_session_early(session_instance):
    session_instance.is_valid = False

    # no exception should be raised
    session_instance.get_connection('vhdxz7abbfirh2lh')


def test_connections(session_instance):
    conns = list(session_instance.connections)

    assert len(conns) == SESSIONS['content'][0]['connections']['numberOfElements']
    assert conns[0].id == SESSIONS['content'][0]['connections']['content'][0]['id']
    assert conns[1].id == SESSIONS['content'][0]['connections']['content'][1]['id']


def test_connections_count(session_instance):
    assert session_instance.connection_count == SESSIONS['content'][0]['connections']['numberOfElements']


def test_connections_count_invalid_session_early(session_instance):
    session_instance.is_valid = False

    # No exception should be raised
    session_instance.connection_count


#
# Signals
#

def test_signal_basic(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=200)

    session_instance.signal('MY_TYPE', "Hello world!")

    assert a.last_request.json() == {
        "session": SESSIONS['content'][0]['id'],
        "type": "MY_TYPE",
        "data": "Hello world!"
    }


def test_signal_extra(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=200)
    connections = list(session_instance.connections)

    session_instance.signal('MY_TYPE', "Hello world!", connections)

    assert a.last_request.json() == {
        "session": SESSIONS['content'][0]['id'],
        "type": "MY_TYPE",
        "data": "Hello world!",
        "to": [connection.id for connection in connections]
    }


def test_signal_value_error(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=400)

    with pytest.raises(ValueError):
        session_instance.signal('MY_TYPE', "Hello world!")

    assert a.called_once
    assert session_instance.is_valid  # user meme


def test_signal_no_session(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.signal('MY_TYPE', "Hello world!")

    assert a.called_once
    assert not session_instance.is_valid


def test_signal_no_session_early(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=404)

    session_instance.is_valid = False

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.signal('MY_TYPE', "Hello world!")

    assert not a.called


def test_signal_no_connection(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=406)

    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        session_instance.signal('MY_TYPE', "Hello world!")

    assert a.called_once
    assert not session_instance.is_valid


#
# IPCAM
#

def test_session_new_ipcam_connection(session_instance, requests_mock):
    new_connection_data = {
        "id": "con_Xnxg19tonh",
        "object": "connection",
        "type": "IPCAM",
        "status": "active",
        "sessionId": "TestSession",
        "createdAt": 1538481999022,
        "activeAt": 1538481999843,
        "platform": "IPCAM",
        "token": None,
        "serverData": "",
        "clientData": None,
        "rtspUri": "rtsp://91.191.213.50:554/live_mpeg4.sdp",
        "adaptativeBitrate": True,
        "onlyPlayWithSubscribers": True,
        "networkCache": 2000,
        "publishers": [
            {
                "createdAt": 1538481999710,
                "streamId": "str_CAM_NhxL_con_Xnxg19tonh",
            }
        ],
        "subscribers": []
    }

    a = requests_mock.post(urljoin(URL_BASE, 'sessions/TestSession/connection'), json=new_connection_data)

    new_connection = session_instance.create_ipcam_connection("rtsp://91.191.213.50:554/live_mpeg4.sdp")

    assert a.last_request.json() == {
        "type": "IPCAM",
        "rtspUri": "rtsp://91.191.213.50:554/live_mpeg4.sdp"
    }

    assert a.called_once

    assert new_connection.id == new_connection_data['id']
    assert new_connection.server_data == new_connection_data['serverData']
    assert new_connection.created_at == datetime.utcfromtimestamp(new_connection_data['createdAt'] / 1000.0)
    assert new_connection.active_at == datetime.utcfromtimestamp(new_connection_data['activeAt'] / 1000.0)
    assert new_connection.rtsp_uri == 'rtsp://91.191.213.50:554/live_mpeg4.sdp'
    assert new_connection.session_id == 'TestSession'

    assert new_connection.publishers[0].created_at == datetime.utcfromtimestamp(
        new_connection_data['publishers'][0]['createdAt'] / 1000.0
    )
    assert new_connection.publishers[0].stream_id == new_connection_data['publishers'][0]['streamId']
    assert new_connection.publishers[0].session_id == 'TestSession'


def test_session_new_ipcam_connection_extra(session_instance, requests_mock):
    new_connection_data = {
        "id": "con_Xnxg19tonh",
        "object": "connection",
        "type": "IPCAM",
        "status": "active",
        "sessionId": "TestSession",
        "createdAt": 1538481999022,
        "activeAt": 1538481999843,
        "platform": "IPCAM",
        "token": None,
        "serverData": "TEST_DATA",
        "clientData": None,
        "rtspUri": "rtsp://91.191.213.50:554/live_mpeg4.sdp",
        "adaptativeBitrate": True,
        "onlyPlayWithSubscribers": True,
        "networkCache": 2000,
        "publishers": [
            {
                "createdAt": 1538481999710,
                "streamId": "str_CAM_NhxL_con_Xnxg19tonh",
            }
        ],
        "subscribers": []
    }

    a = requests_mock.post(urljoin(URL_BASE, 'sessions/TestSession/connection'), json=new_connection_data)

    new_connection = session_instance.create_ipcam_connection(
        "rtsp://91.191.213.50:554/live_mpeg4.sdp",
        "TEST_DATA",
        adaptive_bitrate=False,
        only_play_with_subscribers=True,
        network_cache=1
    )

    assert a.last_request.json() == {
        "type": "IPCAM",
        "rtspUri": "rtsp://91.191.213.50:554/live_mpeg4.sdp",
        "adaptativeBitrate": False,
        "onlyPlayWithSubscribers": True,
        "data": 'TEST_DATA',
        "networkCache": 1
    }

    assert a.called_once

    assert new_connection.id == new_connection_data['id']
    assert new_connection.server_data == new_connection_data['serverData']
    assert new_connection.created_at == datetime.utcfromtimestamp(new_connection_data['createdAt'] / 1000.0)
    assert new_connection.active_at == datetime.utcfromtimestamp(new_connection_data['activeAt'] / 1000.0)
    assert new_connection.rtsp_uri == 'rtsp://91.191.213.50:554/live_mpeg4.sdp'
    assert new_connection.session_id == 'TestSession'

    assert new_connection.publishers[0].created_at == datetime.utcfromtimestamp(
        new_connection_data['publishers'][0]['createdAt'] / 1000.0
    )
    assert new_connection.publishers[0].stream_id == new_connection_data['publishers'][0]['streamId']
    assert new_connection.publishers[0].session_id == 'TestSession'


def test_session_new_ipcam_connection_invalid_session_fail_early(session_instance):
    session_instance.is_valid = False

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.create_ipcam_connection("rtsp://91.191.213.50:554/live_mpeg4.sdp")


def test_session_new_ipcam_connection_invalid_session(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'sessions/TestSession/connection'), json={}, status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.create_ipcam_connection("rtsp://91.191.213.50:554/live_mpeg4.sdp")

    assert a.called_once
    assert not session_instance.is_valid


def test_session_new_ipcam_connection_value_error(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'sessions/TestSession/connection'), json={}, status_code=400)

    with pytest.raises(ValueError):
        session_instance.create_ipcam_connection("rtsp://91.191.213.50:554/live_mpeg4.sdp")

    assert a.called_once
    assert session_instance.is_valid  # user meme


def test_session_new_ipcam_connection_server_error(session_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'sessions/TestSession/connection'), json={}, status_code=500)

    with pytest.raises(OpenViduError):
        session_instance.create_ipcam_connection("rtsp://91.191.213.50:554/live_mpeg4.sdp")

    assert a.called_once
    assert session_instance.is_valid  # It might be valid but the server is borked or something


#
# Fetching
#

def test_fetching_nothing_happened(session_instance):
    is_changed = session_instance.fetch()

    assert not is_changed


def test_fetching_session_became_invalid(session_instance, requests_mock):
    a = requests_mock.get(urljoin(URL_BASE, 'sessions/TestSession'), json={}, status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        session_instance.fetch()

    assert a.called_once
    assert not session_instance.is_valid


def test_fetching_changed(session_instance, requests_mock):
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

    NEW_SESSIONS = deepcopy(SESSIONS)
    NEW_SESSIONS['content'][0]['connections']['content'].append(new_connection)
    NEW_SESSIONS['content'][0]['connections']['numberOfElements'] = len(
        NEW_SESSIONS['content'][0]['connections']['content']
    )

    a = requests_mock.get(urljoin(URL_BASE, 'sessions/TestSession'), json=NEW_SESSIONS['content'][0])

    is_changed = session_instance.fetch()

    assert session_instance.connection_count == NEW_SESSIONS['content'][0]['connections']['numberOfElements']
    assert list(session_instance.connections)[session_instance.connection_count - 1].id == 'con_Xnxg19tonh'

    assert is_changed
    assert a.called_once


def test_fetching_not_changed_fetch_by_parent(openvidu_instance, session_instance, requests_mock):
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
        "publishers": [],
        "subscribers": []
    }

    NEW_SESSIONS = deepcopy(SESSIONS)
    NEW_SESSIONS['content'][0]['connections']['content'].append(new_connection)
    NEW_SESSIONS['content'][0]['connections']['numberOfElements'] = len(
        NEW_SESSIONS['content'][0]['connections']['content']
    )

    a = requests_mock.get(urljoin(URL_BASE, 'sessions'), json=NEW_SESSIONS)

    is_changed = openvidu_instance.fetch()

    # Check against the original, not the modified one
    assert session_instance.connection_count == SESSIONS['content'][0]['connections']['numberOfElements']
    assert len(list(session_instance.connections)) == SESSIONS['content'][0]['connections']['numberOfElements']

    assert is_changed
    assert a.called_once


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
