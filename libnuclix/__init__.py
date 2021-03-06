# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''libnuclix initialization code.'''

__all__ = ['channel',
            'conf',
            'event',
            'logger',
            'module',
            'protocol',
            'server',
            'service',
            'conn',
            'timer',
            'user',
            'var']

def shutdown(code, reason):
    '''Shutdown gracefully.'''

    # Import required Python function.
    from sys import exit

    # Import required libnuclix modules.
    import logger, module, server, conn, var

    logger.info('libnuclix.shutdown(): exiting with code %d: %s' % (code, reason))
    module.unload_all()
    conn.disconnect(code, reason)

    for i in var.servers:
        server.delete(i)

    exit(code)
