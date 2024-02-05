import hashlib
import json
import logging
from django.core.cache import cache
from io import BytesIO, TextIOWrapper
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class ExplicitlyControlledCachedFunction:

    def __init__(self, func: Callable, cache_prefix: str,
                 timeout: Optional[int]):
        self._func = func
        self._cache_prefix = cache_prefix
        self._timeout = timeout

    def __call__(self, *a, **kw):
        key = self._make_key(*a, **kw)
        cached = cache.get(key)
        if cached is not None:
            rv, cached_args = cached
            if cached_args == (a, kw):
                return rv
            # well, we are very unlucky
            logger.error("Cache hash conflict! Please consider whether we should solve it or not %s %r %r",
                         key, cached_args, (a, kw))

        return self.recache(*a, **kw)

    def bypass_cache(self, *a, **kw):
        return self._func(*a, **kw)

    def recache(self, *a, **kw):
        key = self._make_key(*a, **kw)
        rv = self._func(*a, **kw)
        data_to_cache = (rv, (a, kw))
        cache.set(key, data_to_cache, timeout=self._timeout)
        return rv

    def _make_key(self, *a, **kw) -> str:
        buf = BytesIO()
        text_buf = TextIOWrapper(buf, encoding="utf-8")
        json.dump([a, kw], text_buf, ensure_ascii=False,
                  separators=(",", ":"), sort_keys=True)
        text_buf.flush()
        buf.seek(0)
        sha1_obj = hashlib.file_digest(buf, "sha1")
        digest = sha1_obj.hexdigest()
        return self._cache_prefix + digest


def explicitly_cached(*, cache_prefix: Optional[str] = None,
                      timeout: Optional[int] = None):
    """
    the decorated function's arguments must be json serialisable
    """
    def decorator(func):
        if cache_prefix is None:
            cache_prefix_ = f"{func.__module__}.{func.__name__}:"
        else:
            cache_prefix_ = cache_prefix
        return ExplicitlyControlledCachedFunction(func, cache_prefix_, timeout)
    return decorator
