#  nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE

'''Protocol handler. This is quite ugly, and we need to figure out a better way.'''

# Import required Python module.
import os

# Import required Python functions.
from imp import load_source
from thread import start_new_thread

# Import required libnuclix module.
import logger

# Import required libnuclix function.
from libnuclix import shutdown

mod = None
commands = {}

def dispatch(on_thread, command, *args):
    '''Dispatch IRC commands.'''

    global commands

    logger.debug('protocol.dispatch(): dispatching %s (threaded = %s)' % (command, on_thread))

    try:
        if on_thread:
            start_new_thread(commands[command]['first'], args)
        else:
            commands[command]['first'](*args)
    except:
        pass

def attach(command, func):
    '''Attach a function to a command.'''

    global commands

    command = command.upper()

    try:
        test = commands[command]
    except KeyError:
        commands[command] = { 'first' : None }

    if commands[command]['first']:
        return False

    commands[command]['first'] = func
    return True

    logger.debug('protocol.attach(): attached function %s to %s' % (func, command))
    event.dispatch('OnCommandAddfirst', command, func)

def detach(command, func):
    '''Detach a function from a command.'''

    global commands

    command = command.upper()

    commands[command]['first'] = None
    logger.debug('protocol.detach(): detached function %s from %s' % (func, command))

def negotiate_link(conn):
    '''Negotiate the link.'''

    global mod

    mod.negotiate_link(conn)

def load(name):
    '''Load the protocol module.'''

    global mod

    try:
        mod = load_source(name, name)
    except ImportError, e:
        shutdown(os.EX_SOFTWARE, 'protocol unable to load: %s' % e)

    if not hasattr(mod, 'protocol_init'):
        shutdown(os.EX_SOFTWARE, 'protocol does not have entry point')
    elif not hasattr(mod, 'protocol_fini'):
        shutdown(os.EX_SOFTWARE, 'protocol does not have exit point')

    mod.protocol_init()
    logger.info('protocol.load(): protocol %s loaded' % mod.__name__)

def unload():
    '''Unload the protocol module.'''

    global mod

    mod.protocol_fini()
    logger.info('protocol.unload(): protocol %s unloaded' % mod.__name__)
