django-remote-finder
====================

Source: https://github.com/garrison/django-remote-finder

Download: https://pypi.python.org/pypi/django-remote-finder

This is a simple package designed to solve the annoying problem of
having to keep various javascript/css libraries updated within a
Django package.  A ``requirements.txt`` file allows us to specify
external Python dependencies, but there is still no good way to keep
Javascript dependencies outside the repository.  Until now.

Get started by adding the following to ``settings.py``::

    REMOTE_FINDER_CACHE_DIR = '/path/to/staticfile/cache'

    REMOTE_FINDER_RESOURCES = [
        ('jquery-2.0.2.min.js', 'http://code.jquery.com/jquery-2.0.2.min.js', 'sha1:1e0331b6dd11e6b511d2e3d75805f5ccdb3b83df'),
    ]

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'remote_finder.RemoteFinder',
    )

And then e.g. in a template, you can write::

    {% load staticfiles %}
    <script src="{% static "jquery-2.0.2.min.js" %}"></script>

No more need to keep such files in the repository!  ``./manage.py
runserver`` (with ``DEBUG=True``) will download the files as needed, as
will ``./manage.py collectstatic``.

NOTE: the Django documentation says "Static file finders are currently
considered a private interface, and this interface is thus
undocumented."  As such, this package may break unexpectedly in the
future.  See
https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATICFILES_FINDERS
for details.
