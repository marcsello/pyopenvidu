#!/usr/bin/env python

"""Tests for `pyopenvidu` package."""

import pytest
from pyopenvidu import OpenVidu
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
