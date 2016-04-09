# -*- coding: utf-8 -*-

from functools import wraps
from .utils import run_function

class Signal(object):

    def __init__(self, name, doc=''):
        self.name = name
        self.doc = doc
        self.receivers = {}

class Namespace(dict):

    def signal(self, name, doc=None):
        try:
            return self[name]
        except KeyError:
            return self.setdefault(name, Signal(name, doc))

namespace = Namespace()

def clear():
    namespace.clear()

def emit(event, **data):
    if event not in namespace:
        return
    for id, func in namespace[event].receivers.items():
        run_function(func, **data)

def register(event, function):
    assert callable(function), 'Function must be callable.'
    namespace.signal(event).receivers[id(function)] = function

def listen(event):
    def decorator(f):
        @wraps(f)
        def deco(*args, **kwargs):
            register(event, f)
            return f(*args, **kwargs)
        return deco
    return decorator


if __name__ == '__main__':
    def handle_hello(**data):
        print 'received data:', data
    register('hello', handle_hello)
    emit('hello', keyword='world')
