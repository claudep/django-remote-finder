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

hash_func_map = {
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'sha224': hashlib.sha224,
    'sha256': hashlib.sha256,
    'sha384': hashlib.sha384,
    'sha512': hashlib.sha512,
}

class RemoteFinder(BaseFinder):
    def __init__(self):
        self.cache_dir = settings.REMOTE_FINDER_CACHE_DIR
        self.storage = FileSystemStorage(self.cache_dir)
        resources_setting = settings.REMOTE_FINDER_RESOURCES
        if not isinstance(resources_setting, (list, tuple)):
            raise ImproperlyConfigured("settings.REMOTE_FINDER_RESOURCES must be a list or tuple")
        resources = {}
        for resource in resources_setting:
            try:
                path, url, cksm = resource
            except ValueError:
                raise ImproperlyConfigured("Each item in settings.REMOTE_FINDER_RESOURCES must be a tuple of three elements (path, url, cksm).")
            try:
                hash_type, expected_hexdigest = cksm.split(':')
            except ValueError:
                raise ImproperlyConfigured("RemoteFinder checksum `%s` is not in `hash_type:hexdigest` format." % cksm)
            try:
                hash_func = hash_func_map[hash_type]
            except KeyError:
                raise ImproperlyConfigured("RemoteFinder: hash type `%s` unknown" % hash_type)
            resources[path] = (url, hash_func, expected_hexdigest)
        self.resources = resources

    def find(self, path, all=False):
        try:
            fetch_info = self.resources[path]
        except KeyError:
            return []
        self.fetch(path, fetch_info)
        match = self.storage.path(path)
        if all:
            return [match]
        else:
            return match

    def fetch(self, path, fetch_info):
        if self.storage.exists(path):
            return

        url, hash_func, expected_hexdigest = fetch_info

        # download the file
        f = urlopen(url)
        try:
            content = f.read()
        finally:
            f.close()

        # check its hash
        hexdigest = hash_func(content).hexdigest()
        if hexdigest != expected_hexdigest:
            raise Exception("Digest does not match!")

        # save it
        name = self.storage.save(path, ContentFile(content))
        if name != path:
            print("Warning: %r != %r" % (name, path))

    def list(self, ignore_patterns):
        for path, fetch_info in self.resources.items():
            if matches_patterns(path, ignore_patterns):
                continue
            self.fetch(path, fetch_info)
            yield path, self.storage

# fixme: make a way to verify all hashes are correct, either on the cmdline or
# all the time
