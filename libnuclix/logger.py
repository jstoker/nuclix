# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE

'''Logger facility.'''

# Import required Python module.
import logging

# Import required Python function.
from logging import handlers

# Import required libnuclix modules.
import var

# Make these references to the real methods.
debug, info, warning, error, critical = None, None, None, None, None

def get_level():
    '''Get the logging level.'''

    logger_level = var.conf.get('logger', 'level')[0] 

    if logger_level == 'info':
        return logging.INFO
    elif logger_level == 'warning':
        return logging.WARNING
    elif logger_level == 'debug':
        return logging.DEBUG
    elif logger_level == 'error':
        return logging.ERROR
    elif logger_level == 'critical':
        return logging.CRITICAL

    return logging.INFO

def init():
    '''Initialize the logging subsystem.'''

    global debug, info, warning, error, critical

    try:
        path = var.conf.get('logger', 'path')[0]
        max_bytes = var.conf.get('logger', 'max_size')[0]
        backup_count = var.conf.get('logger', 'max_logs')[0]
        lformat = var.conf.get('logger', 'format')[0]
        sformat = var.conf.get('logger', 'stream_format')[0]
    except (var.conf.BlockNotFound, var.conf.VariableNotFound):
        print 'nuclix: logger disabled, missing variables, if you want logging please check your configuration'
        return

    var.log = logging.getLogger('nuclix')

    # Set up logging to stderr if we're in foreground mode.
    if not var.fork:
        stream = logging.StreamHandler()
    else:
        stream = None

    handler = handlers.RotatingFileHandler(filename=path, maxBytes=max_bytes, backupCount=backup_count)
    formatter = logging.Formatter(lformat)

    handler.setFormatter(formatter)

    if stream:
        stream_format = logging.Formatter(sformat)
        stream.setFormatter(stream_format)
        var.log.addHandler(stream)

    var.log.addHandler(handler)
    var.log.setLevel(get_level())

    debug, info, warning = var.log.debug, var.log.info, var.log.warning
    error, critical = var.log.error, var.log.critical
