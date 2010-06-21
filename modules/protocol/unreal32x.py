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

def negotiate_link(conn):
    '''Send the linking data.'''

    conn.push('PASS %s' % conn.server['password'])
    conn.push('PROTOCTL TOKEN NICKv2 VHP NICKIP UMODE2 SJOIN SJOIN2 SJ3 NOQUIT TKLEXT')
    conn.push('SERVER %s 1 :%s' % (conn.server['services_name'], conn.server['services_desc']))

def parse_data(conn, data):
    '''Parse the incoming server data.'''

    global pattern

    parv = []

    try:
        origin, command, target, message = pattern.match(data).groups()
    except AttributeError:
        return

    # Make an IRC parameter argument vector.
    if target:
        parv.append(target)

    parv.append(message)

    print parv

    if command == 'PING':
        m_ping(conn, parv)

    if command == '8':
        m_ping(conn, parv)

    if command == 'PONG':
        m_pong(conn, parv)

    if command == '9':
        m_pong(conn, parv)

    if command == 'AWAY':
        m_away(conn, origin, parv)

    if command == '6':
        m_away(conn, origin, parv)

def m_away(conn, origin, parv):
    '''A user went away.'''

    try:
        var.users[origin]
    except KeyError:
        logger.debug('got a user to be marked away/unaway, but doesnt exist: %s' % origin)
        return

    message = ' '.join(parv[0])

    if message:
        u['away_message'] = message
        u['away_ts'] = time.time()
    else:
        if u['away_message']:
            u['away_message'] = None
            u['away_ts'] = 0

def m_ping(conn, parv):
    '''Reply to PING's.'''

    conn.push(':%s PONG %s %s' % (conn.server['services_name'], conn.server['services_name'], parv[0]))
    return

def m_pong(conn, parv):
    '''Reply to PONG's.'''

    pass

def protocol_init():
    '''Protocol entry point.'''
        
    pass
        
def protocol_fini():
    '''Protocol exit point.'''
                
    pass
