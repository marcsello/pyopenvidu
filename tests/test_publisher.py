#!/usr/bin/env python3

"""Tests for OpenViduConnection object"""

import pytest
from pyopenvidu import OpenVidu, OpenViduStreamDoesNotExistsError, OpenViduSessionDoesNotExistsError, \
    OpenViduStreamError
from urllib.parse import urljoin
from datetime import datetime
from .fixtures import URL_BASE, SESSIONS, SECRET


#
# Unpublish
#

def test_unpublish(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=204)

    connection_instance.publishers[0].force_unpublish()

    assert a.called


def test_unpublish_no_publisher(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=404)

    with pytest.raises(OpenViduStreamDoesNotExistsError):
        connection_instance.publishers[0].force_unpublish()

    assert a.called


def test_unpublish_no_session(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=400)

    with pytest.raises(OpenViduSessionDoesNotExistsError):
        connection_instance.publishers[0].force_unpublish()

    assert a.called


def test_unpublish_ipcam(connection_instance, requests_mock):
    a = requests_mock.delete(urljoin(URL_BASE, 'sessions/TestSession/stream/vhdxz7abbfirh2lh_CAMERA_CLVAU'),
                             json={},
                             status_code=405)

    with pytest.raises(OpenViduStreamError):
        connection_instance.publishers[0].force_unpublish()

    assert a.called


#
# Properties
#

def test_properties(connection_instance):
    p = connection_instance.publishers[0]

    assert p.session_id == SESSIONS['content'][0]['id']
    assert p.stream_id == SESSIONS['content'][0]['connections']['content'][0]['publishers'][0]['streamId']

    assert p.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][0]['connections']['content'][0]['publishers'][0]['createdAt'] / 1000.0
    )

    assert p.media_options == SESSIONS['content'][0]['connections']['content'][0]['publishers'][0]['mediaOptions']


def test_properties_ipcam(openvidu_instance):
    session_instance = openvidu_instance.get_session('TestSession2')
    connection_instance = session_instance.get_connection('ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp')
    p = connection_instance.publishers[0]

    assert p.session_id == SESSIONS['content'][1]['id']
    assert p.stream_id == SESSIONS['content'][1]['connections']['content'][0]['publishers'][0]['streamId']

    assert p.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][1]['connections']['content'][0]['publishers'][0]['createdAt'] / 1000.0
    )

    assert p.media_options == SESSIONS['content'][1]['connections']['content'][0]['publishers'][0]['mediaOptions']
