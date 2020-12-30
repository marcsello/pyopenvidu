=================
About fetching...
=================


.. warning:: In PyOpenVidu version 0.2.0 the dynamic and static objects are changed.
    See     :ref:`migrating` for more information.

    This document contains updated information.

In PyOpenVidu there are two kind of objects: dynamic and static. This section aim to explain the details about this design.

Dynamic and static objects
--------------------------

The **dynamic objects** implement a `fetch()` method that can be used to update it's internal representation.

.. list-table:: Dynamic objects, and methods that change their internal representation
   :widths: 25 25 50
   :header-rows: 1

   * - Object
     - Method
     - Notes

   * - **OpenVidu**
     - `__init__(...)`
     - Upon instantiating this object makes a call to `self.fetch()` to collect initial data. (if not disabled)

   * - **OpenVidu**
     - `fetch()`
     - Updates the internal representation of the that single **OpenVidu** object.

   * - **OpenViduSession**
     - `fetch()`
     - Updates the internal representation of that single **OpenViduSession** object.

   * - **OpenViduConnection**
     - `fetch()`
     - Updates the internal representation of that single **OpenViduConnection** object.


Please note, that although `OpenViduSession.create_webrtc_connection(...)`, `OpenViduSession.create_ipcam_connection(...)` and `OpenVidu.create_session(...)` returns with a new connection or session object, which is even begging added to the appropriate list.
It does not update the internal representation of it's parent (`OpenViduSession.fetch()` or `OpenVidu.fetch()` must be called to update the info of other connections). The reason for this is that the API returns the full object, so a fetch() int the background is not required.


**Static objects** are not designed to update their internal representation, thus not implementing a `fetch()` method.
Such objects should not be reused at all, and must be considered invalid after any changes made to them by other calls.
A new version of those objects could be requested by calling the `fetch()` method of the dynamic object that provides them.


.. list-table:: Static objects and methods that turns them, or their parent invalid
   :widths: 25 25 50
   :header-rows: 1

   * - Object
     - Method
     - Notes

   * - **OpenViduPublisher**
     - `force_unpublish()`
     - Affects other **OpenViduConnection** objects because subscriptions may change as well.

   * - **OpenViduSubscriber**
     -
     -


Reasons
-------

The reason behind this architecture is mainly comes from the fact, that the original Java library, that this library took inspiration from uses the same solution.

Because the OpenVidu server does not expose other endpoints than `GET /api/sessions`, `GET /api/sessions/<SESSION_ID>` and `GET /api/sessions/<SESSION_ID>/connections/<CONNECTION_ID>` by making every object "dynamic" would cause a lot of network overhead by transfering the unwanted information (e.g.: updating a Subscriber object would cause downloading all session data and using only a fraction of it).

Another approach would be to not have an internal representation at all, meaning that every method of every object would cause an API call in the background.
This would be a bad idea for the following reasons:

- The server exposes only the few endpoint mentioned above, causing an excessive overhead.
- Accessing to multiple properties of an object would cause an equal amount of API calls (mostly to the same endpoint in our case) instead of one or zero calls when instantiating the object.
- Error handling would be more complicated. The programmer who uses this library must handle HTTP communication errors when accessing to properties as well as deal with the possibility that the represented object changes between API calls (e.g.: The user disconnects between accessing to `created_at` and `role` properties).
