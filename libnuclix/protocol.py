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

def negotiate_link(conn):
    '''Negotiate the link.'''

    global mod

    mod.negotiate_link(conn)

def parse_data(conn, data):
    '''Parse the data.'''

    global mod

    mod.parse_data(conn, data)

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
    elif not hasattr(mod, 'parse_data'):
        shutdown(os.EX_SOFTWARE, 'protocol does not have parser')

    mod.protocol_init()
    logger.info('protocol.load(): protocol %s loaded' % mod.__name__)

def unload():
    '''Unload the protocol module.'''

    global mod

    mod.protocol_fini()
    logger.info('protocol.unload(): protocol %s unloaded' % mod.__name__)
