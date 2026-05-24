#!/usr/bin/env python
"""
File: singleton.py
Description: A Pythonic Singleton implementation.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

class singleton(object):
     """ A Pythonic Singleton """
     def __new__(cls, *args, **kwargs):
         if '_inst' not in vars(cls):
             cls._inst = object.__new__(cls, *args, **kwargs)
         return cls._inst
