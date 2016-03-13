# -*- coding: utf-8 -*-

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

def emit(event, **data):
    if event not in namespace:
        return
    for id, func in namespace[event].receivers.items():
        func(**data)

def register(event, function):
    assert callable(function), 'Function must be callable.'
    namespace.signal(event).receivers[id(function)] = function

if __name__ == '__main__':
    def handle_hello(**data):
        print 'received data:', data
    register('hello', handle_hello)
    emit('hello', keyword='world')
