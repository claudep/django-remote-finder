import hashlib
try:
    from urllib.request import urlopen
except ImportError:  # Python 2
    from urllib2 import urlopen

from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles.finders import BaseFinder
from django.contrib.staticfiles.utils import matches_patterns
from django.conf import settings

class RemoteFinder(BaseFinder):
    def __init__(self):
        self.cache_dir = settings.REMOTE_FINDER_CACHE_DIR
        self.storage = FileSystemStorage(self.cache_dir)
        resources = settings.REMOTE_FINDER_RESOURCES
        if not isinstance(resources, (list, tuple)):
            raise ImproperlyConfigured("settings.REMOTE_FINDER_RESOURCES must be a list or tuple")
        self.resources = {path: (url, cksm) for path, url, cksm in resources}

    def find(self, path, all=False):
        try:
            url, cksm = self.resources[path]
        except KeyError:
            return []
        else:
            self.fetch(path, url, cksm)
            match = self.storage.path(path)
            if all:
                return [match]
            else:
                return match

    def fetch(self, path, url, cksm):
        if self.storage.exists(path):
            return

        # download the file
        f = urlopen(url)
        try:
            content = f.read()
        finally:
            f.close()

        # check its hash
        digest = hashlib.sha1(content).hexdigest()
        if digest != cksm:
            raise Exception("Digest does not match!")

        # save it
        name = self.storage.save(path, ContentFile(content))
        if name != path:
            print("Warning: %r != %r" % (name, path))

    def list(self, ignore_patterns):
        for path, (url, cksm) in self.resources.items():
            if matches_patterns(path, ignore_patterns):
                continue
            self.fetch(path, url, cksm)
            yield path, self.storage

# fixme: make a way to verify all hashes are correct, either on the cmdline or
# all the time
