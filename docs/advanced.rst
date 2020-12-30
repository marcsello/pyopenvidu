==============
Advanced Usage
==============

Initial Fetching
----------------

It is possible, to disable fetching upon the creation of the `OpenVidu` object.
This can be achieved by setting the `initial_fetch` attribute to `False` when creating the object.
Doing so will cause the newly created `OpenVidu` object to not know anything about the state of the `OpenVidu` server.
Not even knowing if it's possible to connect to it.

Without fetching it is still possible to use the following methods:
 * `create_session()`: No state information is required to start a new session (existance of the session is validated by the server).
 * `get_config()`: The configuration of the server is not stored at all, so this call will always request this from the server.
 * `fetch()`: Well, that one is kind of obvious.

If you are confident that's something you need. You can use this to reduce the number of requests in certain cases. Here are some examples of such a scenario:
 * You are making something, that calls `fetch()` before every operation anyways. This would make an initial fetch pointless, so you can disable it.
 * It is not possible to connect to the `OpenVidu` server during the object creation. Later you will call `fetch()` when it's possible.
 * After creating the `OpenVidu` object you will call `fetch()` instantly.
 * Your program will create a session as soon as the `OpenVidu` object created, and only use that.
 * All you need is getting the config using `get_config()`.

Timeouts
--------

It is possible to setup a timeout for every request instantiated by the `OpenVidu` object.
This can be done by setting the `timeout` attribute when creating the `OpenVidu` instance.

This value is passed to the underlying `Requests` session. For more information of the possible combinations and how they work, see `requests's documentation`_ on this topic.

.. _`requests's documentation`: https://2.python-requests.org/en/latest/user/advanced/#timeouts

The Timeout exceptions raised by `Requests` are not modified in any way, so you have to catch the exceptions raised directly by requests.

Here is an example on using timeouts::

    from pyopenvidu import OpenVidu
    import requests.exceptions

    #  Set both connect and read timeout to 2 sec
    openvidu = OpenVidu(OPENVIDU_URL, OPENVIDU_SECRET, initial_fetch=False, timeout=2)

    try:
        session = openvidu.create_session()

    except requests.exceptions.Timeout:
        print("This didn't work: Operation timed out")

