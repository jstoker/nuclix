# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE

'''Global variables.'''

# Our version and configuration file name.
version, config_file = '0.1a', 'conf/nuclix.conf'

# Fork into the background?
fork = True

# Channel/User/Server hash list.
channels, users, servers = {}, {}, {}

# Loaded modules/timers list.
modules_loaded, timers = [], []

# Configuration parser, connection, and logger instance.
log, conf, conn = None, None, None
