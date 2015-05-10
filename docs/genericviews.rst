Generic views
=============

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

        A string attribute that is the name of the database field that contains the timestamp when the resource was archived. Default ``'datetime'``.

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

.. py:class:: TimemapLinkList(object)

    Returns a queryset list in Memento's TimeMap link format. Can be optionally paginated. Designed to emulate `Django's built-in feed framework <https://docs.djangoproject.com/en/1.8/ref/contrib/syndication/>`_.

    .. py:attribute:: paginate_by

        An optional integer attribute that will trigger the pagination of the
        result set so that each page includes the provided number of objects.

    .. py:method:: get_object(request, url)

        Returns the model object for the provided original URL. Required.

    .. py:method:: get_original_url(obj)

        Returns the original URL that was archived given the model object. Required.

    .. py:method:: memento_list(obj)

        Returns the queryset of archived resources associated with the submitted original URL given its object. Required.

    .. py:method:: memento_datetime(item)

        Returns the timestamp of when an archived resource was retrieved given its object. Required.

    **Example myapp/feeds.py**

    .. code-block:: python

        from memento.timemap import TimemapLinkList


        class ExampleTimemapLinkList(TimemapLinkList):
            """
            A Memento TimeMap that, given a URL, will return a list of archived objects for that page in the archive in link format.

            It is linked to a url that looks like something like:

                url(
                    r'^timemap/link/(?P<url>.*)$',
                    feeds.ExampleTimemapLinkList(),
                    name="timemap-screenshot"
                ),

            """
            paginate_by = 1000

            def get_object(self, request, url):
                return get_object_or_404(Site, url__startswith=url)

            def get_original_url(self, obj):
                return obj.url

            def memento_list(self, obj):
                return Screenshot.objects.filter(site=obj)

            def memento_datetime(self, item):
                return item.timestamp

    **Example response**

    .. code-block:: bash

        $ curl -i http://www.example.com/timemap/http://archivedsite.com/
        HTTP/1.0 200 OK
        Server: Apache/2.2.22 (Ubuntu)
        Content-Type: application/link-format; charset=utf-8

        <http://archivedsite.com/>;rel="original",
         <http://www.pastpages.org/timemap/link/http://archivedsite.com/>
           ; rel="self";type="application/link-format",
         <http://www.example.com/timemap/link/http://archivedsite.com?page=1>
           ; rel="timemap";type="application/link-format",
         <http://www.example.com/timemap/link/http://archivedsite.com/?page=2>
           ; rel="timemap";type="application/link-format",
         <http://www.example.com/timemap/link/http://archivedsite.com/?page=3>
           ; rel="timemap";type="application/link-format",
         <http://www.example.com/timemap/link/http://archivedsite.com/?page=4>
           ; rel="timemap";type="application/link-format"

TimeGateView
------------

.. py:class:: TimeGateView(RedirectView)

    Creates a TimeGate that handles a request with a 'Accept-Datetime' headers and returns a response that redirects to the corresponding Memento.

    .. attribute:: model

        A Django database model where the object will be drawn with a ``Model.objects.filter()`` query. Optional. If you want to provide a more specific list, define the ``queryset`` attribute instead.

    .. attribute:: queryset

        The list of objects that will be provided to the template. Can be any iterable of items, not just a Django queryset. Optional, but if this attribute is not defined the ``model`` attribute must be defined.

    .. py:attribute:: datetime_field

        A string attribute that is the name of the database field that contains the timestamp when the resource was archived. Default ``'datetime'``.

    .. py:attribute:: url_kwarg

        The name for the keyword argument in the URL pattern that will be used to filter the queryset down to objects archived for the resource. Default ``'url'``.

    .. py:attribute:: url_field

        A string attribute that is the name of the database field that contains
        the original URL archived. Defailt ``'url'``.

    .. py:attribute:: timemap_pattern_name

        The name of the URL pattern for this site's TimeMap that, given the original url, is able to reverse to return the location of the map that serves as the directory of all versions of this resource archived by your site. Optional.

    **Example myapp/views.py**

    .. code-block:: python

        from memento.timegate import TimeGateView


        class ExampleTimeGateView(TimeGateView):
            """
            A Memento TimeGate that, given a timestamp, will redirect to the detail page for a screenshot in my example archive

            It is linked to a url that looks like something like:

                url(
                    r'^timegate/(?P<url>.*)$',
                    views.ExampleTimeGateView.as_view(),
                    name="timegate"
                ),

            """
            model = Screenshot
            url_field = 'site__url' # You can walk across ForeignKeys like normal
            datetime_field = 'timestamp'
            timemap_pattern_name = "timemap-screenshot"

    **Example response**

    .. code-block:: bash

        $ curl -X HEAD -i http://www.example.com/timegate/http://archivedsite.com/ --header "Accept-Datetime: Fri, 1 May 2015 00:01:00 GMT"
        HTTP/1.1 302 Moved Temporarily
        Server: Apache/2.2.22 (Ubuntu)
        Link: <http://archivedsite.com/>; rel="original", <http://www.example.com/timemap/link/http://archivedsite.com/>; rel="timemap"; type="application/link-format"
        Location: http://www.example.com/screenshot/100/
        Vary: accept-datetime