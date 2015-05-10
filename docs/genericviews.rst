Generic views
=============

Installation
------------

Before you begin, you should have a Django project `created and configured <https://docs.djangoproject.com/en/dev/intro/install/>`_.

In­stall our library from PyPI, like so:

.. code-block:: bash

    $ pip install django-memento-framework

Edit your ``settings.py`` and add this app to your ``INSTALLED_APPS`` list.

.. code-block:: python

    IN­STALLED_APPS = (
        # ...
        # other apps would be above this of course
        # ...
        'memento',
    )
