import hashlib
import logging
from pathlib import Path
from urllib.request import urlopen

from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles.finders import BaseFinder
from django.contrib.staticfiles.utils import matches_patterns
from django.conf import settings

logger = logging.getLogger(__name__)

hash_func_map = {
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'sha224': hashlib.sha224,
    'sha256': hashlib.sha256,
    'sha384': hashlib.sha384,
    'sha512': hashlib.sha512,
}


class _ResourceInfo:
    hash_verified = False

    def __init__(self, url, hash_func, expected_digest):
        self.url = url
        self.hash_func = hash_func
        self.expected_digest = expected_digest


class RemoteFinder(BaseFinder):
    default_cache_dir = 'remote_finder_cache'

    def __init__(self):
        self.always_verify = getattr(settings, "REMOTE_FINDER_ALWAYS_VERIFY", False)
        self.cache_dir = getattr(settings, "REMOTE_FINDER_CACHE_DIR", None)
        if not self.cache_dir:
            if settings.STATIC_ROOT is None:
                raise ImproperlyConfigured(
                    "Either settings.STATIC_ROOT or settings.REMOTE_FINDER_CACHE_DIR must be defined."
                )
            else:
                self.cache_dir = Path(settings.STATIC_ROOT) / self.default_cache_dir
        self.storage = FileSystemStorage(self.cache_dir)
        try:
            resources_setting = settings.REMOTE_FINDER_RESOURCES
        except AttributeError:
            logger.warning("RemoteFinder is enabled, but settings.REMOTE_FINDER_RESOURCES is not defined.")
            resources_setting = ()
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
            try:
                expected_digest = bytearray.fromhex(expected_hexdigest)
            except ValueError:
                raise ImproperlyConfigured("Cannot parse hex string in settings.REMOTE_FINDER_RESOURCES: `%s`" % expected_hexdigest)
            if len(expected_digest) != hash_func().digest_size:
                raise ImproperlyConfigured("settings.REMOTE_FINDER_RESOURCES: %s digest expected %d bytes but %d provided: `%s`" % (hash_type, hash_func().digest_size, len(expected_digest), expected_hexdigest))
            resources[path] = _ResourceInfo(url, hash_func, expected_digest)
        self.resources = resources

    def find(self, path, all=False):
        try:
            resource_info = self.resources[path]
        except KeyError:
            return []
        self.fetch(path, resource_info)
        match = self.storage.path(path)
        if all:
            return [match]
        else:
            return match

    def fetch(self, path, resource_info):
        if self.storage.exists(path):
            # check to see if the hash has already been verified in the
            # lifetime of this process
            if resource_info.hash_verified and not self.always_verify:
                return

            # verify the hash
            f = self.storage.open(path)
            try:
                content = f.read()
            finally:
                f.close()
            digest = resource_info.hash_func(content).digest()
            if digest == resource_info.expected_digest:
                resource_info.hash_verified = True
                return

            # hash verification failed, so delete it from storage and
            # re-download the file
            logger.info("Hash verification failed, so deleting %s from storage", path)

            # The following line does /not/ raise an exception if the file is
            # already deleted, which is desirable for us as it prevents an
            # error in the case of a race condition.
            self.storage.delete(path)

        # download the file
        logger.info("Downloading %s", resource_info.url)
        f = urlopen(resource_info.url)
        try:
            content = f.read()
        finally:
            f.close()

        # check its hash
        digest = resource_info.hash_func(content).digest()
        if digest != resource_info.expected_digest:
            raise RuntimeError(
                "Digest for %s does not match expected value given in settings"
                ".REMOTE_FINDER_RESOURCES" % resource_info.url
            )

        # save it
        name = self.storage.save(path, ContentFile(content))
        if name == path:
            resource_info.hash_verified = True
        else:
            logger.warning("Save failed: %r != %r", name, path)

    def list(self, ignore_patterns):
        for path, resource_info in self.resources.items():
            if matches_patterns(path, ignore_patterns):
                continue
            self.fetch(path, resource_info)
            yield path, self.storage
