# nuclix -- A minimalistic IRC Service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in ../../docs/LICENSE.

'''Example service. This just adds the client. This is also the module description.'''

# Import required libnuclix modules.
from libnuclix import service
from libnuclix import var
from libnuclix import conf

def module_init():
    '''Module entry point.'''

    try:
        nick = var.conf.get('exampleserv', 'nick')[0]
        user = var.conf.get('exampleserv', 'user')[0]
        host = var.conf.get('exampleserv', 'host')[0]
        real = var.conf.get('exampleserv', 'gecos')[0]
    except (conf.BlockNotFound, conf.VariableNotFound):
        return

    service.add('ExampleServ', nick, user, host, real)

def module_fini():
    '''Module exit point.'''

    service.del('ExampleServ')
