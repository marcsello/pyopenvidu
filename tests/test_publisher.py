#!/usr/bin/env python3

"""Tests for OpenViduConnection object"""

import pytest
from pyopenvidu import OpenViduStreamDoesNotExistsError, OpenViduSessionDoesNotExistsError, \
    OpenViduStreamError
from urllib.parse import urljoin
from datetime import datetime
from .fixtures import URL_BASE, SESSIONS


#
# Unpublish
#

def test_unpublish(webrtc_connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=204)

    webrtc_connection_instance.publishers[0].force_unpublish()

    assert a.called_once


def test_unpublish_no_publisher(webrtc_connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=404)

    with pytest.raises(OpenViduStreamDoesNotExistsError):
        webrtc_connection_instance.publishers[0].force_unpublish()

    assert a.called_once


def test_unpublish_no_session(webrtc_connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=400)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        webrtc_connection_instance.publishers[0].force_unpublish()

    assert a.called_once


def test_unpublish_ipcam(webrtc_connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=405)

    with pytest.raises(OpenViduStreamError):
        webrtc_connection_instance.publishers[0].force_unpublish()

    assert a.called_once


#
# Properties
#

def test_properties(webrtc_connection_instance):
    p = webrtc_connection_instance.publishers[0]

    assert p.session_id == SESSIONS['content'][0]['id']
    assert p.stream_id == SESSIONS['content'][0]['connections']['content'][0]['publishers'][0]['streamId']

    assert p.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][0]['connections']['content'][0]['publishers'][0]['createdAt'] / 1000.0
    )

    assert p.media_options == SESSIONS['content'][0]['connections']['content'][0]['publishers'][0]['mediaOptions']


def test_properties_ipcam(openvidu_instance):
    session_instance = openvidu_instance.get_session('TestSession2')
    webrtc_connection_instance = session_instance.get_connection('ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp')
    p = webrtc_connection_instance.publishers[0]

    assert p.session_id == SESSIONS['content'][1]['id']
    assert p.stream_id == SESSIONS['content'][1]['connections']['content'][0]['publishers'][0]['streamId']

    assert p.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][1]['connections']['content'][0]['publishers'][0]['createdAt'] / 1000.0
    )

    assert p.media_options == SESSIONS['content'][1]['connections']['content'][0]['publishers'][0]['mediaOptions']
