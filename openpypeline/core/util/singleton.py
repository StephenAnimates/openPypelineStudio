"""Provide a base class that caches one instance per subclass.

:File: singleton.py
:License: Apache License 2.0 (Apache-2.0)

Usage Example::

    from openpypeline.singleton import singleton

    class PipelineManager(singleton):
        pass

    a = PipelineManager()
    b = PipelineManager()
    assert a is b
"""

from typing import Any

class singleton:
    """Base class implementing the Singleton design pattern.

    Subclasses of :class:`singleton` instantiate only once. Any subsequent instantiation calls return the cached instance stored on the subclass.

    :cvar _inst: Cached singleton instance stored per subclass.
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> "singleton":
        """Return the cached instance for this subclass, creating it if needed.

        :param args: Positional arguments forwarded to ``__init__``.
        :param kwargs: Keyword arguments forwarded to ``__init__``.
        :returns: The single cached instance of ``cls``.
        """
        if "_inst" not in vars(cls):
            cls._inst = object.__new__(cls)
        return cls._inst
