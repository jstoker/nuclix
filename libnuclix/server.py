# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE

'''Server management.'''

# Import required libnuclix modules.
import logger
import var

def add(name, hops, uplink, sid, desc):
    '''Add a server.'''

    if name in var.servers:
        logger.debug('attempted to add server %s already exists' % name)
        return

    if uplink in var.servers:
        logger.debug('attempted to add server %s originating from %s that already exists' % (name, uplink['name']))
        return

    if uplink:
        if not name:
            logger.info('adding server %s (%s) [masked]' % (uplink['name'], sid))
        elif sid:
            logger.info('adding server %s (%s) [uplink %s]' % (name, sid, uplink['name']))
        else:
            logger.info('adding server %s [uplink %s]' % (name, uplink['name']))
    else:
        logger.info('adding server %s [root]' % name)
