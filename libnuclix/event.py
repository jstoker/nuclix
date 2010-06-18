# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''Provide a dynamic event system.'''

# Import required libnuclix module.
import logger

# Event data.
events = {}

def dispatch(name, *args):
    '''Dispatch an event to it's attached function.'''

    global events

    # Call every function attached to 'name'.
    try:
        for func in events[name]['funcs']:
            func(*args)
    except KeyError:
        # Either this event doesn't exist, or there's no functions attached to it. This isn't a bad thing,
        # we just need to do nothing.
        pass

def attach(event, func):
    '''Add a function to an event.'''

    global events

    try:
        test = events[event]
    except KeyError:
        events[event] = { 'funcs' : [] }

    if func in events[event]['funcs']:
        return True

    events[event]['funcs'].append(func)
    return True

    logger.debug('event.attach(): attached function %s to event %s' % (func, event))

def detach(event, func):
    '''Remove a function from an event.'''

    global events

    if func not in events[event]['funcs']:
        return False

    events[event]['funcs'].remove(func)
    logger.debug('event.detach(): detached function %s from event %s' % (func, event))

def find(name):
    '''Find an event created.'''

    global events

    try:
        test = events[name]
    except KeyError:
        return False

    return True
