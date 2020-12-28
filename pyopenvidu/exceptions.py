# Base exception


class OpenViduError(BaseException):
    pass


# Session errors

class OpenViduSessionError(OpenViduError):
    pass


class OpenViduSessionDoesNotExistsError(OpenViduSessionError):
    pass


class OpenViduSessionExistsError(OpenViduSessionError):
    pass


# Connection errors

class OpenViduConnectionError(OpenViduSessionError):
    pass


class OpenViduConnectionDoesNotExistsError(OpenViduConnectionError):
    pass


# Stream errors

class OpenViduStreamError(OpenViduConnectionError):
    pass


class OpenViduStreamDoesNotExistsError(OpenViduStreamError):
    pass
