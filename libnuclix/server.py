# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE

'''Server management.'''

# Import required libnuclix modules.
import logger

def add(name, hops, uplink, sid, desc):
    '''Add a server.'''

    if name in var.servers:
        logger.debug('server.add(): server %s already exists' % name)
        return
    elif uplink in var.servers:
        logger.debug('server.add(): server %s originating from %s already exists' % (name, uplink['name']))
        return

    if uplink:
        if not name:
            logger.info('server.add(): %s (%s) [masked]' % (uplink['name'], sid))
        elif sid:
            logger.info('server.add(): %s (%s) [uplink %s]' % (name, sid, uplink['name']))
        else:
            logger.info('server.add(): %s [uplink %s]' % (name, uplink['name']))
    else:
        logger.info('server.add(): %s [root]' % name)

