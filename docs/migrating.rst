.. _migrating:

=========
Migrating
=========

This page summarizes breaking changes between versions in order to help developers migrating to a newer version of PyOpenVidu.

From 0.1.4 to 0.2.0
===================

With the release of OpenVidu 2.16.0, the REST API of the OpenVidu server changed a lot in various ways.
This has proven that it is not safe make any assumptions about how stable this API will be in the future.

Without any guarantee about said stability. The architecture of the PyOpenVidu library had to be made a little loose in order help adopting later changes.


Because this release must bring changes to the interface of this library (because of the above described reasons), a few more other modifications are added in, to make make the library more maintainable, straightforward to use and less prone to errors.

Behavioural changes
-------------------

Although many things changed, the followings only affect your program in a few edge-cases. And only minor changes are required in those cases as well.

Fetching the OpenVidu object no longer updates the existing session objects
```````````````````````````````````````````````````````````````````````````
This was a broken design to begin with. Originally if you called `fetch()` on the OpenVidu instance, it would update all other instances of `OpenViduSession`. This required the OpenVidu object to keep the reference for each `OpenViduSession` object. Which meant very tight coupling of those objects. This tight coupling caused more problems than it should.

First of all thread safety caused a huge issue when those objects are accessed from different threads (Python's GIL saved most of the headaches, but this still could cause strange behavior). In order to solve this problem, a shared lock between objects was used (See the next section) which not just caused performance issues, but was hard to maintain as well.

Second was the rigid architecture of how the updating of internal representations processed, was an awkward point when the OpenVidu REST API changed in version 2.16.0. Because OpenVidu REST API is not stable, and can change even in minor versions, such a rigid architecture is not a good idea to keep.

Thirdly, this behaviour also caused confusion for software developers, because it is different from what one might expect.

Because of the above outlined issues, this feature was removed: A `fetch()` call on the "parent" object (Not in terms of OOP) no longer cause the update of the information stored in their "children".

If you need to update many OpenVidu session objects in batch, you should call `fetch()` on the OpenVidu instance itself, and use the `sessions` property, to access the updated list of sessions.

If you only need to update a few `OpenViduSession` objects, you should use their `fetch()` method instead, as it's more efficient.


The interface is no longer thread safe.
```````````````````````````````````````
This was more like side-effect of the above mentioned (and now removed) half-solution to a problem that should not exist.
With that feature removed, using locks no longer made sense.

Instead of that the developer who is using the library should have a control over how and when locks are used. This is a better approach in many ways:

- The developer can use any type of lock they want, so that it will work on any framework they might want to use (Multiprocessing, Qt's QThreads, etc.) not just plain Python threads.
- Because of the nature of this library it won't be unlikely that after some call that changes the data of a class (e.g.: `fetch()`) one may access to more than one properties. Because an internal lock would lock those individually it might be possible for another thread to change the value of the properties before they are read after changing it on the other thread. In this scenario an external lock would be needed anyway, so an internal one would be useless.
- No unwanted side effects of the unexpected locks.

Because of the above mentioned reasons, this feature is now removed.


Connection object is now dynamic
````````````````````````````````
Well this is not a breaking change, but it's important to mention. As of OpenVidu release 2.16.0 it is possible to fetch info about a connection directly.
This made it possible to implement `fetch()` for the connection object as well.


Base URL must include the `/api/` part
`````````````````````````````````````
Originally the `/api/` part was appended to the base url by the library itself. This was needed because there was a single endpoint which could not be reached under `/api` (`config`). But with OpenVidu release 2.16.0 this endpoint was moved bellow `/api`.
This allows more freedom of your reverse proxy and server configuration.

If you previously passed `https://my.openvidu.instance.com:4443/` to the constructor of the `OpenVidu` object. Now you have to pass `https://my.openvidu.instance.com:4443/openvidu/api/`. (The `/openvidu/` part was added in the new release of OpenVidu as well)

Creating a new session no longer does an internal fetch() call
``````````````````````````````````````````````````````````````
As of OpenVidu release 2.16.0 the API returns the created session object. This allows PyOpenVidu to return with the newly created `OpenViduSession` object without fetching it first.

The new object is also being added to the `OpenVidu.sessions` list, but the other sessions are not being updated at this point.

Properties no longer fail if the object is invalid
``````````````````````````````````````````````````
Before this release. An object might raised an exception when it was invalid and specific properties are accessed. (e.g.: connection_count of the OpenViduSession instance, and stuff like that).

This was a kind of inconsistent behaviour because not every property implemented it. And by rewriting parts of the code to use dataclasses instead of properties implemented one-by-one it would require ugly hacks to achieve.

This also introduced an unnecessary limitation, because invalid object's properties could not be used while in some scenarios this would be useful. Also programmers had to write unnecessary try-except blocks around all code that access properties/getters because it was not clear which ones may fail and which may not.
Because of this inconsistency this was a perfectly useless restriction.

Because of the above mentioned reasons this behaviour is removed. From now on getters/properties won't raise any exception if they are being used. Allowing the use of those values even if the object became invalid.


Changes of the interface
------------------------

Two type of connections

The following tables summarize the changes of various classe's methods and properties.

OpenViduSession
```````````````

.. list-table::
   :widths: 45 45 10
   :header-rows: 1

   * - Old attribute
     - New attribute
     - Notes

   * - `(method)` :code:`generate_token(role, data, video_max_recv_bandwidth, video_min_recv_bandwidth, video_max_send_bandwidth, video_min_send_bandwidth, allowed_filters -> str`
     - `(method)` :code:`create_webrtc_connection(role, data, video_max_recv_bandwidth, video_min_recv_bandwidth, video_max_send_bandwidth, video_min_send_bandwidth, allowed_filters) -> OpenViduWEBRTCConnection`
     - Token is now a property of the `OpenViduWEBRTCConnection` returned.

   * - `(method)` :code:`publish(rtsp_uri, data, adaptive_bitrate, only_play_with_subscribers, type_) -> OpenViduConnection`
     - `(method)` :code:`create_ipcam_connection(rtsp_uri, data, adaptive_bitrate, only_play_with_subscribers, network_cache) -> OpenViduIPCAMConnection`
     - `type_` is removed A new parameter `network_cache` is added. Also default values not provided.

   * - `(property)` :code:`connections -> Iterator[OpenViduConnection]`
     - `(property)` :code:`connections -> List[OpenViduConnection]`
     - This property is changed to a `List` from `Iterator`.

OpenViduConnection
``````````````````

.. list-table::
   :widths: 25 50 25
   :header-rows: 1

   * - Old attribute
     - New attribute
     - Notes

   * - N/A
     - `(property)` :code:`fetch() -> bool`
     - Connection objects became dynamic.

   * - N/A
     - `(property)` :code:`is_valid -> bool`
     - Connection objects became dynamic.

   * - N/A
     - `(property)` :code:`publisher_count -> int`
     - Added for convenience.

   * - N/A
     - `(property)` :code:`subscriber_count -> int`
     - Added for convenience.

OpenViduPublisher
`````````````````

.. list-table::
   :widths: 45 45 10
   :header-rows: 1

   * - Old attribute
     - New attribute
     - Notes

   * - `(property)` :code:`rtsp_uri -> str`
     - `(property)` :code:`OpenViduIPCAMConnection.rtsp_uri -> str`
     - This property is moved from the publisher to the connection object itself.
