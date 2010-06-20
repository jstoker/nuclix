# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''Unreal 3.2.x protocol.'''

# Import required Python modules.
import time
import re

# Import required libnuclix modules.
from libnuclix import event
from libnuclix import var
from libnuclix import server
from libnuclix import logger
from libnuclix import protocol
from libnuclix import channel

# A regular expression to match and dissect IRC protocol messages.
# This is actually around 60% faster than not using RE.
pattern = r'''
             ^              # beginning of string
             (?:            # non-capturing group
                 \:         # if we have a ':' then we have an origin
                 ([^\s]+)   # get the origin without the ':'
                 \s         # space after the origin
             )?             # close non-capturing group
             (\w+)          # must have a command
             \s             # and a space after it
             (?:            # non-capturing group
                 ([^\s\:]+) # a target for the command
                 \s         # and a space after it
             )?             # close non-capturing group
             (?:            # non-capturing group
                 \:?        # if we have a ':' then we have freeform text
                 (.*)       # get the rest as one string without the ':'
             )?             # close non-capturing group
             $              # end of string
            '''

# Note that this doesn't match *every* IRC message,
# just the ones we care about. It also doesn't match
# every IRC message in the way we want. We get what
# we need. The rest is ignored.
#
# Here's a compact version if you need it:
#     ^(?:\:([^\s]+)\s)?(\w+)\s(?:([^\s\:]+)\s)?(?:\:?(.*))?$
pattern = re.compile(pattern, re.VERBOSE)

def protocol_init():
    '''Protocol entry point.'''
        
    pass
        
def protocol_fini():
    '''Protocol exit point.'''
                
    pass
