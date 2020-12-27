#!/usr/bin/env python3

"""Tests for OpenViduConnection object"""

import pytest
from pyopenvidu import OpenVidu, OpenViduSessionDoesNotExistsError, OpenViduConnectionDoesNotExistsError
from urllib.parse import urljoin
from datetime import datetime
from .fixtures import URL_BASE, SESSIONS, SECRET

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
