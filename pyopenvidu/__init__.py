"""Top-level package for PyOpenVidu."""

__author__ = """Marcell Pünkösd"""
__email__ = 'punkosdmarcell@rocketmail.com'
__version__ = '0.2.0'

from .openvidu import OpenVidu

from .exceptions import OpenViduError, OpenViduSessionError, OpenViduSessionDoesNotExistsError, OpenViduConnectionError, \
    OpenViduConnectionDoesNotExistsError, OpenViduStreamError, OpenViduStreamDoesNotExistsError, OpenViduSessionExistsError
