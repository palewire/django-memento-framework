import urllib
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from dateutil.parser import parse as dateparser
from django.utils.cache import patch_vary_headers
from django.utils.translation import ugettext as _
from memento.templatetags.memento_tags import httpdate
from django.core.exceptions import ImproperlyConfigured
from django.contrib.syndication.views import add_domain
from django.contrib.sites.models import get_current_site
from django.views.generic import RedirectView, DetailView


class MementoDetailView(DetailView):
    """
    Extends Django's DetailView to describe an archived resource.

    A set of extra headers is added to the response. They are:

        * The "Memento-Datetime" when the resource was archived.

        * A "Link" that includes the URL of the original resource as well
          as the location of the TimeMap the publishes the directory of
          all versions archived by your site.

        * A "Vary" indicator that this is a Memento enabled site

    The view should be subclassed and configured like any other DetailView
    with a few extra options. They are:

        * datetime_field: A string attribute that is the name of the database
          field that contains the timestamp when the resource was archived.

        * timemap_pattern: The name of the URL pattern for this site's TimeMap
          that, given the original url, is able to reverse to return the
          location of the map that serves as the directory of all versions of
          this resource archived by your site.

        * get_original_url: A method that, given the object being rendered
          by the view, will return the original URL of the archived resource.

    """
    datetime_field = 'datetime'
    timemap_pattern_name = None

    def get_timemap_url(self, request, url):
        """
        Returns the location of the TimeMap that lists resources archived
        for the provided URL.
        """
        path = reverse(self.timemap_pattern_name, kwargs={'url': url})
        current_site = get_current_site(request)
        return add_domain(
            current_site.domain,
            path,
            request.is_secure(),
        )

    def get_original_url(self, obj):
        raise NotImplementedError("get_original_url method not implemented")

    def get(self, request, *args, **kwargs):
        response = super(MementoDetailView, self).get(
            request,
            *args,
            **kwargs
        )
        dt = getattr(self.object, self.datetime_field)
        response['Memento-Datetime'] = httpdate(dt)
        patch_vary_headers(response, ["accept-datetime"])
        if self.timemap_pattern_name:
            original_url = self.get_original_url(self.object)
            timemap_url = self.get_timemap_url(self.request, original_url)
            response['Link'] = """<%(original_url)s>; rel="original", \
<%(timemap_url)s>; rel="timemap"; type="application/link-format\"""" % dict(
                original_url=urllib.unquote(original_url),
                timemap_url=urllib.unquote(timemap_url)
            )
        return response


class TimeGateView(RedirectView):
    """
    Creates a TimeGate that handles a request with Memento headers
    and returns a response that redirects to the corresponding
    Memento.
    """
    model = None
    queryset = None
    timemap_pattern_name = None
    url_kwarg = 'url'
    url_field = 'url'
    datetime_field = 'datetime'

    def parse_datetime(self, request):
        """
        Parses the requested datetime from the request headers
        and returns it if it exists. Otherwise returns None.
        """
        # Verify that the Accept-Datetime header is provided
        if not request.META.get("HTTP_ACCEPT_DATETIME"):
            return None

        # Verify that the Accept-Datetime header is valid
        dt = dateparser(request.META.get("HTTP_ACCEPT_DATETIME"))
        if not dt:
            return HttpResponse(
                _("Bad request (400): Accept-Datetime header is malformed"),
                status=400
            )
        return dt

    def get_object(self, url, dt):
        """
        Accepts the requested URL and datetime and returns the object
        with the smallest date difference.
        """
        queryset = self.get_queryset()
        queryset = queryset.filter(**{self.url_field: url})

        try:
            prev_obj = queryset.filter(
                **{"%s__lte" % self.datetime_field: dt}
            ).order_by("-%s" % self.datetime_field)[0]
        except IndexError:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        try:
            next_obj = queryset.filter(
                **{"%s__gte" % self.datetime_field: dt}
            ).order_by("%s" % self.datetime_field)[0]
        except IndexError:
            next_obj = None

        if not next_obj:
            return prev_obj
        else:
            prev_delta = abs(dt - getattr(prev_obj, self.datetime_field))
            next_delta = abs(dt - getattr(next_obj, self.datetime_field))
            if prev_delta <= next_delta:
                return prev_obj
            else:
                return next_obj

    def get_most_recent_object(self, url):
        """
        Returns the most recently archive object of the submitted URL
        """
        queryset = self.get_queryset()
        try:
            return queryset.filter(**{
                self.url_field: url,
            }).order_by("-%s" % self.datetime_field)[0]
        except IndexError:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

    def get_queryset(self):
        """
        Return the `QuerySet` that will be used to look up the object.
        Note that this method is called by the default implementation of
        `get_object` and may not be called if `get_object` is overridden.
        """
        if self.queryset is None:
            if self.model:
                return self.model._default_manager.all()
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.model, %(cls)s.queryset, or override "
                    "%(cls)s.get_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )
        return self.queryset.all()

    def get_redirect_url(self, request, obj):
        """
        Returns the URL that will redirect to the Memento resource.
        """
        current_site = get_current_site(request)
        return add_domain(
            current_site.domain,
            obj.get_absolute_url(),
            request.is_secure(),
        )

    def get_timemap_url(self, request, url):
        """
        Returns the location of the TimeMap that lists resources archived
        for the provided URL.
        """
        path = reverse(self.timemap_pattern_name, kwargs={'url': url})
        current_site = get_current_site(request)
        return add_domain(
            current_site.domain,
            path,
            request.is_secure(),
        )

    def get(self, request, *args, **kwargs):
        url = self.kwargs.get(self.url_kwarg)
        if not url:
            return HttpResponse(
                _("Bad request (400): URL not provided"),
                status=400
            )
        url = url.replace("http:/", "http://")
        url = url.replace("http:///", "http://")
        dt = self.parse_datetime(request)
        if dt:
            obj = self.get_object(url, dt)
        else:
            obj = self.get_most_recent_object(url)
        redirect_url = self.get_redirect_url(request, obj)
        response = HttpResponse(status=302)
        patch_vary_headers(response, ["accept-datetime"])
        if self.timemap_pattern_name:
            response['Link'] = """<%(url)s>; rel="original", \
<%(timemap_url)s>; rel="timemap"; type="application/link-format\"""" % dict(
                url=urllib.unquote(url),
                timemap_url=urllib.unquote(self.get_timemap_url(request, url))
            )
        response['Location'] = urllib.unquote(redirect_url)
        return response
