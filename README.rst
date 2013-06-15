django-remote-finder
====================

This is a simple package designed to solve the annoying problem of
having to keep various javascript/css libraries updated within a
Django package.  A ``requirements.txt`` file allows us to specify
external Python dependencies, but there is still no good way to keep
Javascript dependencies outside the repository.  Until now.

Get started by adding the following to ``settings.py``::

    REMOTE_FINDER_CACHE_DIR = '/path/to/staticfile/cache'

    REMOTE_FINDER_RESOURCES = [
        ('jquery-2.0.2.min.js', 'http://code.jquery.com/jquery-2.0.2.min.js', '1e0331b6dd11e6b511d2e3d75805f5ccdb3b83df'),
    ]

And then e.g. in a template, you can write::

    {% load staticfiles %}
    <script src="{% static "jquery-2.0.2.min.js" %}"></script>

and the script will automatically download.  No more need to keep it
in the repository!

NOTE: `Static file finders are currently considered a private
interface, and this interface is thus
undocumented.<https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATICFILES_FINDERS>`_
