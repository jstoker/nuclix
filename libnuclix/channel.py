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
import event

def add(name, ts):
    '''Add the channel to the hash list.'''

    if name in var.channels:
        logger.debug('attempted to add a channel that already exists: %s' % name)
        return

    var.channels[name] = { 'ts'           : 0,
                           'ucount'       : 0,
                           'users'        : [],
                           'topic'        : None,
                           'topic_setter' : None,
                           'metadata'     : [] }

    var.channels[name]['ts'] = ts
    logger.debug('channel %s created' % name)

def delete(name):
    '''Delete a channel.'''

    if name not in var.channels:
        logger.debug('got a channel that doesnt exist: %s' % name)
        return

    var.channels[name]['ts'] = 0
    var.channels[name]['ucount'] = 0
    var.channels[name]['users'] = []
    var.channels[name]['topic'] = None
    var.channels[name]['topic_setter'] = None
    var.channels[name]['metadata'] = []

def delete_user(channel, user):
    '''Remove a user from a channel.'''

    try:
        var.channels[channel]
    except KeyError:
        logger.debug('attempted to remove user %s from channel %s, but that channel does not exist' % (user['nick'], channel))
        return

    event.dispatch('OnUserPart', channel, user)

    var.channels[name]['ucount'] -= 1

    if var.channels[name]['ucount'] == 0:
        logger.debug('channel %s became empty after %s parted, removing' % (channel['name'], user['nick']))
        delete_channel(channel)

    logger,debug('user %s from %s removed' % (user['nick'], channel['name']))

def delete_channel(channel):
    '''Remove a channel, it's users, everything.'''

    try:
        var.channels[channel]
    except KeyError:
        logger.debug('attempted to delete non-existant channel %s' % channel)
        return

    event.dispatch('OnDeleteChannel', channel)

    var.channels[channel]['ts'] = 0
    var.channels[channel]['ucount'] = 0
    var.channels[channel]['users'] = []
    var.channels[channel]['topic'] = None
    var.channels[channel]['topic_setter'] = None
    var.channels[channel]['metadata'] = []

    logger.debug('deleted channel %s' % channel['name'])

def maintain():
    '''Maintain the channels, sorting them out, etc.'''

    for i in var.channels:
        var.channels[i]['metadata'].sort()
        var.channels[i]['users'].sort()
