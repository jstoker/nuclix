# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''Channel management.'''

# Import required Python function.
from time import time

# Import required libnuclix modules.
import var
import logger
import protocol

def add(name):
    '''Add the channel to the hash list.'''

    if not name.startswith(protocol.chan_prefixes):
        logger.debug('channel.add(): got a channel with an invalid prefix: %s' % name)
        return

    if name in var.channels:
        logger.debug('channel.add(): channel already exists: %s' % name)
        return

    var.channels[name] = { 'ts'           : 0,
                           'ucount'       : 0,
                           'users'        : [],
                           'topic'        : None,
                           'topic_setter' : None,
                           'metadata'     : [] }

    var.channels[name]['ts'] = time()
    logger.debug('channel.add(): %s' % name)

def delete(name):
    '''Delete a channel.'''

    if name not in var.channels:
        logger.debug('channel.delete(): got a channel that doesnt exist: %s' % name)
        return

    var.channels[name]['ts'] = 0
    var.channels[name]['ucount'] = 0
    var.channels[name]['users'] = []
    var.channels[name]['topic'] = None
    var.channels[name]['topic_setter'] = None
    var.channels[name]['metadata'] = []

def maintain():
    '''Maintain the channels, sorting them out, etc.'''

    for i in var.channels:
        var.channels[i]['metadata'].sort()
        var.channels[i]['users'].sort()