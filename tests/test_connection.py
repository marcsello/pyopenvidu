#!/usr/bin/env python3

"""Tests for OpenViduConnection object"""

import pytest
from copy import deepcopy
from pyopenvidu import OpenViduSessionDoesNotExistsError, OpenViduConnectionDoesNotExistsError
from urllib.parse import urljoin
from datetime import datetime
from .fixtures import URL_BASE, SESSIONS


#
# Fetching
#

def test_webrtc_fetching_nothing_changed(webrtc_connection_instance, requests_mock):
    a = requests_mock.get(
        urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'),
        json=SESSIONS['content'][0]['connections']['content'][0]
    )
    is_changed = webrtc_connection_instance.fetch()

    assert a.called_once
    assert not is_changed


def test_webrtc_fetching_data_changed_changed(webrtc_connection_instance, requests_mock):
    NEW_SESSIONS = deepcopy(SESSIONS)

    NEW_SESSIONS['content'][0]['connections']['content'][0]['subscribers'].append(
        {
            "streamId": "str_CAM_NhxL_con_Xnasd9t23h",
            "createdAt": 1538482000857
        }
    )

    a = requests_mock.get(
        urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'),
        json=NEW_SESSIONS['content'][0]['connections']['content'][0]
    )
    is_changed = webrtc_connection_instance.fetch()

    assert a.called_once
    assert is_changed


def test_webrtc_fetching_connection_no_longer_exists(webrtc_connection_instance, requests_mock):
    a = requests_mock.get(
        urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'),
        status_code=404
    )

    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        webrtc_connection_instance.fetch()

    assert a.called_once
    assert not webrtc_connection_instance.is_valid


def test_webrtc_fetching_session_no_longer_exists(webrtc_connection_instance, requests_mock):
    a = requests_mock.get(
        urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'),
        status_code=400
    )

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        webrtc_connection_instance.fetch()

    assert a.called_once
    assert not webrtc_connection_instance.is_valid


def test_webrtc_fetching_fail_early(webrtc_connection_instance, requests_mock):
    webrtc_connection_instance.is_valid = False

    a = requests_mock.get(
        urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'),
        status_code=404
    )

    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        webrtc_connection_instance.fetch()

    assert not a.called
    assert not webrtc_connection_instance.is_valid


def test_ipcam_fetching_nothing_changed(ipcam_connection_instance, requests_mock):
    a = requests_mock.get(
        urljoin(URL_BASE, 'sessions/TestSession2/connection/ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp'),
        json=SESSIONS['content'][1]['connections']['content'][0]
    )
    is_changed = ipcam_connection_instance.fetch()

    assert a.called_once
    assert not is_changed


#
# Disconnection
#

def test_disconnection(webrtc_connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'), json={},
                             status_code=204)

    webrtc_connection_instance.force_disconnect()

    assert a.called_once
    assert not webrtc_connection_instance.is_valid


def test_disconnection_failed_no_connection(webrtc_connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'), json={},
                             status_code=404)

    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        webrtc_connection_instance.force_disconnect()

    assert a.called_once
    assert not webrtc_connection_instance.is_valid


def test_disconnection_failed_no_connection_early(webrtc_connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'), json={},
                             status_code=404)

    webrtc_connection_instance.is_valid = False
    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        webrtc_connection_instance.force_disconnect()

    assert not a.called


def test_disconnection_failed_no_session(webrtc_connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/connection/vhdxz7abbfirh2lh'), json={},
                             status_code=400)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        webrtc_connection_instance.force_disconnect()

    assert a.called_once
    assert not webrtc_connection_instance.is_valid


#
# Signals
#

def test_signal(webrtc_connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=200)

    webrtc_connection_instance.signal('MY_TYPE', "Hello world!")

    assert a.called_once
    assert a.last_request.json() == {
        "session": SESSIONS['content'][0]['id'],
        "type": "MY_TYPE",
        "data": "Hello world!",
        "to": [SESSIONS['content'][0]['connections']['content'][0]['id']]

    }


def test_signal_value_error(webrtc_connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=400)

    with pytest.raises(ValueError):
        webrtc_connection_instance.signal('MY_TYPE', "Hello world!")

    assert a.called_once
    assert webrtc_connection_instance.is_valid  # It was user error, the session should be still valid


def test_signal_no_session(webrtc_connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=404)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        webrtc_connection_instance.signal('MY_TYPE', "Hello world!")

    assert a.called_once
    assert not webrtc_connection_instance.is_valid


def test_signal_no_connection(webrtc_connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=406)

    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        webrtc_connection_instance.signal('MY_TYPE', "Hello world!")

    assert a.called_once
    assert not webrtc_connection_instance.is_valid


def test_signal_no_connection_early(webrtc_connection_instance, requests_mock):
    a = requests_mock.post(urljoin(URL_BASE, 'signal'), status_code=406)

    webrtc_connection_instance.is_valid = False
    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        webrtc_connection_instance.signal('MY_TYPE', "Hello world!")

    assert not a.called


#
# Unpublish
#

def test_force_unpublish_all(webrtc_connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=204)

    webrtc_connection_instance.force_unpublish_all_streams()

    assert a.called_once


def test_force_unpublish_all_no_connection_early(webrtc_connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=204)

    webrtc_connection_instance.is_valid = False
    with pytest.raises(OpenViduConnectionDoesNotExistsError):
        webrtc_connection_instance.force_unpublish_all_streams()

    assert not a.called


#
# Properties
#

def test_webrtc_connection_is_valid_true(webrtc_connection_instance):
    assert webrtc_connection_instance.is_valid


def test_ipcam_connection_is_valid_true(webrtc_connection_instance):
    assert webrtc_connection_instance.is_valid


def test_webrtc_connection_properties(webrtc_connection_instance):
    # Common part

    assert webrtc_connection_instance.id == SESSIONS['content'][0]['connections']['content'][0]['id']
    assert webrtc_connection_instance.session_id == SESSIONS['content'][0]['id']
    assert webrtc_connection_instance.type == "WEBRTC"

    assert webrtc_connection_instance.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][0]['connections']['content'][0]['createdAt'] / 1000.0
    )

    assert webrtc_connection_instance.active_at == datetime.utcfromtimestamp(
        SESSIONS['content'][0]['connections']['content'][0]['activeAt'] / 1000.0
    )

    assert webrtc_connection_instance.platform == SESSIONS['content'][0]['connections']['content'][0]['platform']
    assert webrtc_connection_instance.server_data == SESSIONS['content'][0]['connections']['content'][0]['serverData']

    assert webrtc_connection_instance.publisher_count == len(
        SESSIONS['content'][0]['connections']['content'][0]['publishers']
    )

    assert webrtc_connection_instance.subscriber_count == len(
        SESSIONS['content'][0]['connections']['content'][0]['subscribers']
    )

    assert len(webrtc_connection_instance.publishers) == len(
        SESSIONS['content'][0]['connections']['content'][0]['publishers']
    )

    assert len(webrtc_connection_instance.subscribers) == len(
        SESSIONS['content'][0]['connections']['content'][0]['subscribers']
    )

    # WEBRTC specific part

    assert webrtc_connection_instance.token == SESSIONS['content'][0]['connections']['content'][0]['token']
    assert webrtc_connection_instance.client_data == SESSIONS['content'][0]['connections']['content'][0]['clientData']
    assert webrtc_connection_instance.role == SESSIONS['content'][0]['connections']['content'][0]['role']

    assert webrtc_connection_instance.kurento_options == \
           SESSIONS['content'][0]['connections']['content'][0]['kurentoOptions']

    # IPCAM only fields

    with pytest.raises(AttributeError):
        webrtc_connection_instance.rtsp_uri

    with pytest.raises(AttributeError):
        webrtc_connection_instance.adaptive_bitrate

    with pytest.raises(AttributeError):
        webrtc_connection_instance.only_play_with_subscribers

    with pytest.raises(AttributeError):
        webrtc_connection_instance.network_cache


def test_webrtc_connection_none_fields(session_instance):
    webrtc_connection_instance = session_instance.get_connection(
        SESSIONS['content'][0]['connections']['content'][2]['id'])

    assert webrtc_connection_instance.active_at is None
    assert webrtc_connection_instance.client_data is None
    assert webrtc_connection_instance.server_data is None
    assert len(webrtc_connection_instance.publishers) == 0
    assert len(webrtc_connection_instance.subscribers) == 0


def test_ipcam_connection_properties(ipcam_connection_instance):
    # Common part

    assert ipcam_connection_instance.id == SESSIONS['content'][1]['connections']['content'][0]['id']
    assert ipcam_connection_instance.session_id == SESSIONS['content'][1]['id']
    assert ipcam_connection_instance.type == "IPCAM"

    assert ipcam_connection_instance.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][1]['connections']['content'][0]['createdAt'] / 1000.0
    )

    assert ipcam_connection_instance.active_at == datetime.utcfromtimestamp(
        SESSIONS['content'][1]['connections']['content'][0]['activeAt'] / 1000.0
    )

    assert ipcam_connection_instance.platform == SESSIONS['content'][1]['connections']['content'][0]['platform']
    assert ipcam_connection_instance.server_data == SESSIONS['content'][1]['connections']['content'][0]['serverData']

    assert ipcam_connection_instance.publisher_count == len(
        SESSIONS['content'][1]['connections']['content'][0]['publishers']
    )

    assert ipcam_connection_instance.subscriber_count == len(
        SESSIONS['content'][1]['connections']['content'][0]['subscribers']
    )

    assert len(ipcam_connection_instance.publishers) == len(
        SESSIONS['content'][1]['connections']['content'][0]['publishers']
    )

    assert len(ipcam_connection_instance.subscribers) == len(
        SESSIONS['content'][1]['connections']['content'][0]['subscribers']
    )

    # IPCAM specific part

    assert ipcam_connection_instance.rtsp_uri == SESSIONS['content'][1]['connections']['content'][0]['rtspUri']

    assert ipcam_connection_instance.adaptive_bitrate == \
           SESSIONS['content'][1]['connections']['content'][0]['adaptativeBitrate']

    assert ipcam_connection_instance.only_play_with_subscribers == \
           SESSIONS['content'][1]['connections']['content'][0]['onlyPlayWithSubscribers']

    assert ipcam_connection_instance.network_cache == SESSIONS['content'][1]['connections']['content'][0][
        'networkCache']

    # WEBRTC only fields

    with pytest.raises(AttributeError):
        ipcam_connection_instance.token

    with pytest.raises(AttributeError):
        ipcam_connection_instance.client_data

    with pytest.raises(AttributeError):
        ipcam_connection_instance.role

    with pytest.raises(AttributeError):
        ipcam_connection_instance.kurento_options
