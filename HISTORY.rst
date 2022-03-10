=======
History
=======

0.2.1 (2022-03-10)
------------------

* Added `cert` and `verify` options to the OpenVidu object constructor.
* Various fixes in the documentation
* Included Python 3.10 in the test suite

0.2.0 (2020-12-30)
------------------

* Implemented OpenVidu REST API version 2.16.0.
* Removed inter-object update
* Changed Base URL
* Removed broken "Thread safety" approach
* See the "Migrating" section of the documentation on how to update your code.

0.1.4 (2020-05-24)
------------------

* Added timeouts.
* Added possibility to disable initial fetching.
* Fixed some mistakes in the documentation.
* Reached 100% code coverage.


0.1.3 (2020-04-26)
------------------

* Implemented thread safety for the dynamic objects.
* Added IPCAM publishing option.
* Updated and restructured documentation.

0.1.2 (2020-04-07)
------------------

* Removed publisher property of the OpenViduSubscriber object, as it was removed from the OpenVidu Server as well.

0.1.1 (2020-04-04)
------------------

* Fixed dependencies not being automatically installed.
* Updated classifiers and URLs for PyPI.
* Added more tests and updated existing ones.

0.1.0 (2020-04-03)
------------------

* First release on PyPI.
* Implemented support for most of the endpoints except recording and IPCam stuff.
