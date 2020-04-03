=================
About fetching...
=================

In PyOpenVidu there are two kind of objects: dynamic and static. This section aim to explain the details about this design.

Dynamic and static objects
--------------------------

The dynamic objects implement a `fetch()` method that can be used to update it's internal representation.
Sometimes those objects have such a function that updates the internal representation as a side effect.



.. list-table:: Dynamic objects, and methods that change their internal representation
   :widths: 25 25 50
   :header-rows: 1

   * - Object
     - Method
     - Notes

   * - **OpenVidu**
     - `__init__(...)`
     - Upon instantiating this object makes a call to `self.fetch()` to collect initial data.

   * - **OpenVidu**
     - `fetch()`
     - Updates the internal representation of all **OpenViduSession** objects.

   * - **OpenVidu**
     - `create_session(...)`
     - This method calls `self.fetch()` automatically since the server does not return the proper data to construct the OpenViduSession object.

   * - **OpenViduSession**
     - `fetch()`
     - Updates the internal representation of that single **OpenViduSession** object

   * - **OpenViduSession**
     - `close()`
     - This deletes the internal representation of that Session. All methods after this call will raise `OpenViduSessionDoesNotExistsError` exception, except `is_valid`

Static objects are not designed to update their internal representation, thus not implementing a `fetch()` method.
Such objects should not be reused at all, and must be considered invalid after any changes made to them by other calls.
A new version of those objects could be requested by calling the `fetch()` method of the dynamic object that provides them.


.. list-table:: Static objects and methods that turns them, or their parent invalid
   :widths: 25 25 50
   :header-rows: 1

   * - Object
     - Method
     - Notes

   * - **OpenViduConnection**
     - `force_disconnect()`
     - Affects other **OpenViduConnection** objects because subscriptions may change as well.

   * - **OpenViduConnection**
     - `force_unpublish_all_streams()`
     - Affects other **OpenViduConnection** objects because subscriptions may change as well.

   * - **OpenViduPublisher**
     - `force_unpublish()`
     - Affects other **OpenViduConnection** objects because subscriptions may change as well.

   * - **OpenViduSubscriber**
     -
     -


Reasons
-------

The reason behind this architecture is mainly comes from the fact, that the original Java library, that this library took inspiration from uses the same solution.

Because the OpenVidu server does not expose other endpoints than `GET /api/sessions` and `GET /api/sessions/<SESSION_ID>` by making every object "dynamic" would cause a lot of network overhead by transfering the unwanted information (e.g.: updating a Subscriber object would cause downloading all session data and using only a fraction of it).

Another approach would be to not have an internal representation at all, meaning that every method of every object would cause an API call in the background.
This would be a bad idea for the following reasons:

- The server exposes only the two endpoint mentioned above, causing an excessive overhead
- Accessing to multiple properties of an object would cause an equal amount of API calls (mostly to the same endpoint in our case) instead of one or zero calls when instantiating the object.
- Error handling would be more complicated. The programmer who uses this library must handle HTTP communication errors when accessing to properties as well as deal with the possibility that the represented object changes between API calls (e.g.: The user disconnects between accessing to `created_at` and `role` properties)

Since the `fetch()` method of the **OpenVidu** object updates the internal representation of every valid **OpenViduSession** object and returns a boolean indicating if anything changed means, that the **OpenVidu** object have read and write the representation stored in the **OpenViduSession** objects.
If every all objects would be "dynamic" that would mean that the **OpenVidu** object would have to somehow get the information stored in all objects in order to compare if anything changed, and write the updated information back to every object. In most cases this would add an unnecessary complexity to the library itself, as well as causing way too many wasted cpu cycles for accessing objects never used.
The comparision couldn't be solved by storing all information in the objects because that multiple-source-of-truth would introduce even more unwanted complexity as the information must be kept consistent.
