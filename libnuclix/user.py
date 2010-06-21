# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''User management.'''

# Import required source modules.
import logger

def add(nick, ident, host, gecos, vhost, ip, uid, server, ts):
    '''Add a user.'''

    logger.debug('adding user %s!%s@%s [%s]' % (nick, ident, host, server['name']))

    if var.users[nick]:
        logger.debug('attempted to add user %s which already exists' % nick)
        return
