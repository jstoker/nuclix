# nuclix -- A minimalistic IRC Service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in ../../docs/LICENSE.

'''Example service. This just adds the client. This is also the module description.'''

# Import required libnuclix modules.
from libnuclix import service
from libnuclix import protocol

def cmd_example(service, user, params):
    '''Handle the example command.'''

    protocol.notice(service['nick'], user['nick'], 'This is an example command.')
    return

def module_init():
    '''Module entry point.'''
    
    service.add_command('EXAMPLE', cmd_example, 'ExampleServ')

def module_fini():
    '''Module exit point.'''

    service.del_command('EXAMPLE', cmd_example, 'ExampleServ')
