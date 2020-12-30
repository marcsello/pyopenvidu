import pytest
from urllib.parse import urljoin
from pyopenvidu import OpenVidu

URL_BASE = 'http://test.openvidu.io:4443/openvidu/api/'
SECRET = 'MY_SECRET'

SESSIONS = {
    "numberOfElements": 2,
    "content": [
        {
            "id": "TestSession",
            "object": "session",
            "createdAt": 1538481996019,
            "mediaMode": "ROUTED",
            "recordingMode": "MANUAL",
            "defaultOutputMode": "COMPOSED",
            "defaultRecordingLayout": "CUSTOM",
            "defaultCustomLayout": "",
            "customSessionId": "TestSession",
            "connections": {
                "numberOfElements": 3,
                "content": [
                    {
                        "id": "vhdxz7abbfirh2lh",
                        "object": "connection",
                        "type": "WEBRTC",
                        "status": "active",
                        "sessionId": "TestSession",
                        "createdAt": 1538481999022,
                        "activeAt": 1538481999843,
                        "location": "",
                        "platform": "Chrome 85.0.4183.102 on Linux 64-bit",
                        "token": "wss://localhost:4443?sessionId=TestSession&token=tok_AVe8o7iltWqtijyl&role=PUBLISHER&version=2.16.0&coturnIp=localhost&turnUsername=M2ALIY&turnCredential=7kfjy2",
                        "serverData": "My Server Data",
                        "clientData": "My Client Data",
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
                            {
                                "createdAt": 1538481999710,
                                "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU",
                                "mediaOptions": {
                                    "hasAudio": True,
                                    "audioActive": True,
                                    "hasVideo": True,
                                    "videoActive": True,
                                    "typeOfVideo": "CAMERA",
                                    "frameRate": 30,
                                    "videoDimensions": "{\"width\":640,\"height\":480}",
                                    "filter": {}
                                }
                            }
                        ],
                        "subscribers": [
                            {
                                "streamId": "str_CAM_NhxL_con_Xnasd9tonh",
                                "createdAt": 1538482000856
                            }
                        ]
                    },
                    {
                        "id": "maxawc4zsuj1rxva",
                        "object": "connection",
                        "type": "WEBRTC",
                        "status": "active",
                        "sessionId": "TestSession",
                        "createdAt": 1538481999022,
                        "activeAt": 1538481999843,
                        "location": "",
                        "platform": "Chrome 69.0.4183.102 on Linux 64-bit",
                        "token": "wss://localhost:4443?sessionId=TestSession&token=tok_AVe8o7iltWqtijyl&role=PUBLISHER&version=2.16.0&coturnIp=localhost&turnUsername=M2ALIY&turnCredential=7kfjy2",
                        "serverData": None,
                        "clientData": None,
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
                            {
                                "createdAt": 1538481999710,
                                "streamId": "str_CAM_NhxL_con_Xnasd9tonh",
                                "mediaOptions": {
                                    "hasAudio": True,
                                    "audioActive": True,
                                    "hasVideo": True,
                                    "videoActive": True,
                                    "typeOfVideo": "CAMERA",
                                    "frameRate": 30,
                                    "videoDimensions": "{\"width\":640,\"height\":480}",
                                    "filter": {}
                                }
                            }
                        ],
                        "subscribers": [
                            {
                                "streamId": "vhdxz7abbfirh2lh_CAMERA_CLVAU",
                                "createdAt": 1538482000856
                            }
                        ]
                    },
                    {
                        "id": "unconnectedconnection",
                        "object": "connection",
                        "type": "WEBRTC",
                        "status": "active",
                        "sessionId": "TestSession",
                        "createdAt": 1538481999022,
                        "activeAt": None,
                        "location": "",
                        "platform": "Chrome 69.0.4183.102 on Linux 64-bit",
                        "token": "wss://localhost:4443?sessionId=TestSession&token=tok_AVe8o7iltWqtijyl&role=PUBLISHER&version=2.16.0&coturnIp=localhost&turnUsername=M2ALIY&turnCredential=7kfjy2",
                        "serverData": None,
                        "clientData": None,
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
                        "publishers": None,
                        "subscribers": None
                    }

                ]
            },
            "recording": False
        },
        {
            "id": "TestSession2",
            "object": "session",
            "createdAt": 1538481996020,
            "mediaMode": "ROUTED",
            "recordingMode": "ALWAYS",
            "defaultOutputMode": "COMPOSED",
            "defaultRecordingLayout": "CUSTOM",
            "defaultCustomLayout": "",
            "customSessionId": "TestSession2",
            "connections": {
                "numberOfElements": 1,
                "content": [
                    {
                        "id": "ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp",
                        "object": "connection",
                        "type": "IPCAM",
                        "status": "active",
                        "sessionId": "TestSession2",
                        "createdAt": 1538481919022,
                        "activeAt": 1538481009843,
                        "location": "",
                        "platform": "IPCAM",
                        "token": None,
                        "serverData": "My Server Data",
                        "clientData": "My Client Data",
                        "record": True,
                        "rtspUri": "rtsp://user:pass@example.com",
                        "adaptativeBitrate": True,
                        "onlyPlayWithSubscribers": False,
                        "networkCache": 2000,
                        "publishers": [
                            {
                                "createdAt": 1538481999711,
                                "streamId": "str_CAM_NhxL_con_Xnxg123qnh",
                                "mediaOptions": {
                                    "hasAudio": False,
                                    "audioActive": False,
                                    "hasVideo": True,
                                    "videoActive": True,
                                    "typeOfVideo": "CAMERA",
                                    "frameRate": 15,
                                    "videoDimensions": "{\"width\":640,\"height\":480}",
                                    "filter": {}
                                }
                            }
                        ],
                        "subscribers": []
                    }

                ]
            },
            "recording": True
        }
    ]}


@pytest.fixture
def openvidu_instance(requests_mock):
    requests_mock.get(urljoin(URL_BASE, 'sessions'), json=SESSIONS)
    requests_mock.get(urljoin(URL_BASE, 'sessions/TestSession'), json=SESSIONS['content'][0])
    requests_mock.get(urljoin(URL_BASE, 'sessions/TestSession2'), json=SESSIONS['content'][1])
    yield OpenVidu(URL_BASE, SECRET)


@pytest.fixture
def session_instance(openvidu_instance):
    yield openvidu_instance.get_session('TestSession')


@pytest.fixture
def webrtc_connection_instance(session_instance):
    yield session_instance.get_connection('vhdxz7abbfirh2lh')


@pytest.fixture
def ipcam_connection_instance(openvidu_instance):
    session_instance = openvidu_instance.get_session('TestSession2')
    yield session_instance.get_connection('ipc_IPCAM_rtsp_A8MJ_91_191_213_49_554_live_mpeg4_sdp')
