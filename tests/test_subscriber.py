#!/usr/bin/env python3

"""Tests for OpenViduConnection object"""

import pytest
from datetime import datetime
from .fixtures import SESSIONS


#
# Properties
#


def test_properties(webrtc_connection_instance):
    s = webrtc_connection_instance.subscribers[0]

    assert s.session_id == SESSIONS['content'][0]['id']
    assert s.stream_id == SESSIONS['content'][0]['connections']['content'][0]['subscribers'][0]['streamId']

    assert s.created_at == datetime.utcfromtimestamp(
        SESSIONS['content'][0]['connections']['content'][0]['subscribers'][0]['createdAt'] / 1000.0
    )
