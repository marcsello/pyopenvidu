#!/usr/bin/env python3

"""Tests for OpenViduConnection object"""

import pytest
from pyopenvidu import OpenViduSessionDoesNotExistsError, OpenViduConnectionDoesNotExistsError
from urllib.parse import urljoin
from datetime import datetime
from .fixtures import URL_BASE, SESSIONS


#
# Disconnection
#

def test_disconnection(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'), json={},
                             status_code=204)

    connection_instance.force_disconnect()

    assert a.called_once


def test_disconnection_failed_no_connection(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'), json={},
                             status_code=404)

    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        connection_instance.force_disconnect()

    assert a.called_once


def test_disconnection_failed_no_session(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'), json={},
                             status_code=400)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        connection_instance.force_disconnect()

    assert a.called_once


#
# Signals
#

def test_signal(connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=200)

    connection_instance.signal('MY_TYPE', "Hello world!")

    assert a.called_once
    assert a.last_request.json() == {
        "session": SESSIONS['content'][0]['id'],
        "type": "MY_TYPE",
        "data": "Hello world!",
        "to": [SESSIONS['content'][0]['connections']['content'][0]['id']]

    }


def test_signal_value_error(connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=400)

    with pytest.raises(ValueError):
        connection_instance.signal('MY_TYPE', "Hello world!")

    assert a.called_once


def test_signal_no_session(connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        connection_instance.signal('MY_TYPE', "Hello world!")

    assert a.called_once


def test_signal_no_connection(connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=406)

    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        connection_instance.signal('MY_TYPE', "Hello world!")

    assert a.called_once


#
# Unpublish
#

def test_force_unpublish_all(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=204)

    connection_instance.force_unpublish_all_streams()

    assert a.called_once


#
# Properties
#

def test_properties(connection_instance):
    assert connection_instance.session_id == SESSIONS['content'][0]['id']
    assert connection_instance.id == SESSIONS['content'][0]['connections']['content'][0]['id']

    assert connection_instance.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][0]['connections']['content'][0]['createdAt'] / 1000.0
    )

    assert connection_instance.token == SESSIONS['content'][0]['connections']['content'][0]['token']
    assert connection_instance.client_data == SESSIONS['content'][0]['connections']['content'][0]['clientData']
    assert connection_instance.server_data == SESSIONS['content'][0]['connections']['content'][0]['serverData']
    assert connection_instance.platform == SESSIONS['content'][0]['connections']['content'][0]['platform']
    assert connection_instance.role == SESSIONS['content'][0]['connections']['content'][0]['role']

    assert connection_instance.publisher_count == len(SESSIONS['content'][0]['connections']['content'][0]['publishers'])
    assert connection_instance.subscriber_count == len(
        SESSIONS['content'][0]['connections']['content'][0]['subscribers']
    )

    assert len(connection_instance.publishers) == len(SESSIONS['content'][0]['connections']['content'][0]['publishers'])


def test_properties_none_fields(session_instance):
    connection_instance = session_instance.get_connection(SESSIONS['content'][0]['connections']['content'][1]['id'])

    assert connection_instance.session_id == SESSIONS['content'][0]['id']
    assert connection_instance.id == SESSIONS['content'][0]['connections']['content'][1]['id']

    assert connection_instance.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][0]['connections']['content'][0]['createdAt'] / 1000.0
    )

    assert connection_instance.token == SESSIONS['content'][0]['connections']['content'][1]['token']
    assert connection_instance.client_data is None
    assert connection_instance.server_data is None
    assert connection_instance.platform == SESSIONS['content'][0]['connections']['content'][1]['platform']
    assert connection_instance.role == SESSIONS['content'][0]['connections']['content'][1]['role']

    assert connection_instance.publisher_count == len(SESSIONS['content'][0]['connections']['content'][0]['publishers'])
    assert connection_instance.subscriber_count == len(
        SESSIONS['content'][0]['connections']['content'][0]['subscribers']
    )

    assert len(connection_instance.publishers) == len(SESSIONS['content'][0]['connections']['content'][1]['publishers'])


def test_properties_ipcam_fields(openvidu_instance):
    session_instance = openvidu_instance.get_session(SESSIONS['content'][1]['id'])
    connection_instance = session_instance.get_connection(SESSIONS['content'][1]['connections']['content'][0]['id'])

    assert connection_instance.session_id == SESSIONS['content'][1]['id']
    assert connection_instance.id == SESSIONS['content'][1]['connections']['content'][0]['id']

    assert connection_instance.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][1]['connections']['content'][0]['createdAt'] / 1000.0
    )

    assert connection_instance.server_data == SESSIONS['content'][1]['connections']['content'][0]['serverData']
    assert connection_instance.platform == SESSIONS['content'][1]['connections']['content'][0]['platform']

    assert connection_instance.publisher_count == len(SESSIONS['content'][1]['connections']['content'][0]['publishers'])
    assert connection_instance.subscriber_count == len(
        SESSIONS['content'][1]['connections']['content'][0]['subscribers']
    )

    assert len(connection_instance.publishers) == len(SESSIONS['content'][1]['connections']['content'][0]['publishers'])
