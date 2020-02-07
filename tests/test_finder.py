import os
import shutil

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template
from django.test import modify_settings, SimpleTestCase


class FinderTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        finders.get_finder.cache_clear()
        shutil.rmtree(settings.REMOTE_FINDER_CACHE_DIR, ignore_errors=True)

    def test_missing_cache_dir(self):
        msg = "settings.REMOTE_FINDER_CACHE_DIR must point to a cache directory."
        with self.settings():
            del settings.REMOTE_FINDER_CACHE_DIR
            with self.assertRaisesMessage(ImproperlyConfigured, msg):
                finder = finders.get_finder('remote_finder.RemoteFinder')

    def test_missing_resources(self):
        msg = "settings.REMOTE_FINDER_RESOURCES must point to a cache directory."
        with self.settings():
            del settings.REMOTE_FINDER_RESOURCES
            with self.assertLogs('remote_finder', level='WARN') as cm:
                finder = finders.get_finder('remote_finder.RemoteFinder')
            self.assertEqual(cm.output, [
                'WARNING:remote_finder:RemoteFinder is enabled, but '
                'settings.REMOTE_FINDER_RESOURCES is not defined.'
            ])

    def test_finder_find(self):
        finder = finders.get_finder('remote_finder.RemoteFinder')
        path = finder.find('js/jquery.min.js')
        self.assertEqual(
            path,
            os.path.join(settings.REMOTE_FINDER_CACHE_DIR, 'js', 'jquery.min.js')
        )
        # No match
        path = finder.find('js/jquery.js')
        self.assertEqual(path, [])

    def test_finder_list(self):
        finder = finders.get_finder('remote_finder.RemoteFinder')
        listed = list(finder.list([]))
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0][0], 'js/jquery.min.js')
        file_path = os.path.join(settings.REMOTE_FINDER_CACHE_DIR, 'js', 'jquery.min.js')
        self.assertTrue(os.path.exists(file_path))

    def test_render(self):
        t = Template('''{% load static %}<script src="{% static 'js/jquery.min.js' %}">''')
        result = t.render(Context({}))
        self.assertEqual(result, '<script src="js/jquery.min.js">')

    @modify_settings(REMOTE_FINDER_RESOURCES={
        'append': [(
            'js/jquery.min2.js',
            'https://code.jquery.com/jquery-3.3.1.min.js',
            'sha1:2885e21e33426ab1c8c8e587b038e713521cc3da'
        )],
    })
    def test_bad_checksum(self):
        finder = finders.get_finder('remote_finder.RemoteFinder')
        msg = (
            'Digest for https://code.jquery.com/jquery-3.3.1.min.js does not '
            'match expected value given in settings.REMOTE_FINDER_RESOURCES'
        )
        with self.assertRaisesMessage(RuntimeError, msg):
            path = finder.find('js/jquery.min2.js')
