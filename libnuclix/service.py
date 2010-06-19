# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''Service (pseudoclient) handlers.'''

# Import required libnuclix modules.
import logger

def add(name):
    '''Add a service.'''

    if name in var.services:
        logger.debug('attempted to add service %s that already exists' % name)
        return

    var.services[name] = { 'nick'     : None,
                           'user'     : None,
                           'host'     : None,
                           'gecos'    : None,
                           'commands' : {} }

    logger.info('service %s created' % name)

def del(name):
    '''Delete a service.'''

    if name not in var.services:
        logger.debug('attempted to delete service %s that doesnt exist' % name)
        return

    var.services[name]['nick'] = None
    var.services[name]['user'] = None
    var.services[name]['host'] = None
    var.services[name]['gecos'] = None
    var.services[name]['commands'] = {}

    logger.info('service %s removed' % name)

def add_command(name, cmd, func):
    '''Add a command to a service.'''

    pass

def del_command(name, cmd, func):
    '''Delete a command from a service.'''

    pass
