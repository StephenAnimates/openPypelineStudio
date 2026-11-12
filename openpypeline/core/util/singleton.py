#!/usr/bin/env python

class singleton(object):
     """ A Pythonic Singleton """
     def __new__(cls, *args, **kwargs):
         """Return the one instance cached for this singleton class."""
         if '_inst' not in vars(cls):
             cls._inst = object.__new__(cls, *args, **kwargs)
         return cls._inst
