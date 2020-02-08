import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


APP_DIR = os.path.abspath(os.path.dirname(__file__))

SETTINGS_DICT = {
    'TEMPLATES': [{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
    }],
    'STATIC_ROOT': os.path.join(APP_DIR, 'static'),
    'STATICFILES_FINDERS': [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'remote_finder.RemoteFinder',
    ],
    'REMOTE_FINDER_RESOURCES': [
        ('js/jquery.min.js', 'https://code.jquery.com/jquery-3.3.1.min.js', 'sha1:0dc32db4aa9c5f03f3b38c47d883dbd4fed13aae'),
    ],
    'REMOTE_FINDER_CACHE_DIR': os.path.join(APP_DIR, 'tests', 'cache'),
}

def run_tests():
    settings.configure(**SETTINGS_DICT)
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    run_tests()
