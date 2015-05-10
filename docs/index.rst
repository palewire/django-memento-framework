django-memento-framework
========================

A set for helpers for Django web sites to enable `the Memento framework <http://www.mementoweb.org/guide/quick-intro/>`_ for time-based access.

How does it work?
-----------------

Django's `class-based views <https://docs.djangoproject.com/en/dev/topics/class-based-views/>`_  are used to retrieve archived data and format it according to `Memento's rules <http://www.mementoweb.org/guide/quick-intro/>`_.

The generic views in this package can be used to quickly:

* Publish a TimeMap that lists all of the archived versions of each URL in your archive
* Host a TimeGate that handles requests that include a URL and a timestamp, redirecting to the detail view for the nearest archive
* Enrich detail views in the archive to include the extra metadata required by the Memento system

Documentation
-------------

.. toctree::
   :maxdepth: 3

   gettingstarted
   genericviews
   changelog

Other resources
---------------

* Code repository: `github.com/pastpages/django-memento-framework <https://github.com/pastpages/django-memento-framework>`_
* Issues: `github.com/pastpages/django-memento-framework/issues <https://github.com/pastpages/django-memento-framework/issues>`_
* Packaging: `pypi.python.org/pypi/django-memento-framework <https://pypi.python.org/pypi/django-memento-framework>`_
* Testing: `travis-ci.org/pastpages/django-memento-framework <https://travis-ci.org/pastpages/django-memento-framework>`_
* Coverage: `coveralls.io/r/pastpages/django-memento-framework <https://coveralls.io/r/pastpages/django-memento-framework>`_