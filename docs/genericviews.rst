Generic views
=============

Django's `class-based views <https://docs.djangoproject.com/en/dev/topics/class-based-views/>`_  are used to query data and format it according to `Memento's rules <http://www.mementoweb.org/guide/quick-intro/>`_.

Putting all the pieces together is a little tricky at first, particularly if you haven't studied `the Django source code <https://github.com/django/django/tree/master/django/views/generic>`_ or lack experience `working with Python classes <http://www.diveintopython.net/object_oriented_framework/defining_classes.html>`_ in general.

But if you figure it out, we think it's worth the trouble.

MementoDetailView
-----------------

.. py:class:: MementoDetailView(DetailView)

    Extends Django's generic `DetailView <https://docs.djangoproject.com/en/dev/ref/class-based-views/base/#django.views.generic.base.DetailView>`_ to describe an archived resource.

    A set of extra headers is added to the response. They are:

        * The ``Memento-Datetime`` when the resource was archived.

        * A ``Link`` that includes the URL of the original resource as well
          as the location of the TimeMap the publishes the directory of
          all versions archived by your site.

        * A ``Vary`` indicator that this is a Memento enabled site

    .. py:attribute:: datetime_field

        A string attribute that is the name of the database field that contains the timestamp when the resource was archived. Required.

    .. py:attribute:: timemap_pattern_name

        The name of the URL pattern for this site's TimeMap that, given the original url, is able to reverse to return the location of the map that serves as the directory of all versions of this resource archived by your site. Optional.

    .. py:method:: get_original_url()

        A method that, given the object being rendered by the view, will return the original URL of the archived resource.

    **Example myapp/views.py**

    .. code-block:: python

        from memento.timegate import MementoDetailView

        class ExampleMementoDetailView(MementoDetailView):
            """
            A Memento-enabled detail page for a screenshot in my example
            archive.

            It is linked to a url that looks like something like:

                url(
                    r'^screenshot/(?P<pk>\d+)/$',
                    views.ExampleMementoDetailView.as_view(),
                    name='screenshot-detail'
                )

            """
            model = Screenshot
            datetime_field = 'timestamp'
            timemap_pattern_name = "timemap-screenshot"

            def get_original_url(self, obj):
                return obj.site.url

    **Example response**

    .. code-block:: bash

        $ curl -X HEAD -i http://www.example.com/screenshot/100/
        HTTP/1.1 200 OK
        Server: Apache/2.2.22 (Ubuntu)
        Link: <http://archivedsite.com/>; rel="original", <http://www.example.com/timemap/link/http://archivedsite.com/>; rel="timemap"; type="application/link-format"
        Memento-Datetime: Fri, 1 May 2015 00:00:01 GMT
        Vary: accept-datetime


TimemapLinkList
---------------


TimeGateView
------------