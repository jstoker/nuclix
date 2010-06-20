# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''Service (pseudoclient) handlers.'''

# Import required libnuclix modules.
import logger
import protocol

def add(name, nick, ident, host, gecos):
    '''Add a service.'''

    if name in var.services:
        logger.debug('attempted to add service %s that already exists' % name)
        return

    var.services[name] = { 'nick'     : None,
                           'user'     : None,
                           'host'     : None,
                           'gecos'    : None,
                           'commands' : {} }

    var.services[name]['nick'] = nick
    var.services[name]['ident'] = ident
    var.services[name]['host'] = host
    var.services[name]['gecos'] = gecos

    logger.info('service %s created' % name)

    # Now introduce it to the network.
    protocol.introduce_service(var.services[name])

def delete(name):
    '''Delete a service.'''

    if name not in var.services:
        logger.debug('attempted to delete service %s that doesnt exist' % name)
        return

    # Remove the service from the network before removing the commands.
    protocol.quit(name, 'service removed')

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
