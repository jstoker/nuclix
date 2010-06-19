# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''Charybdis IRCd protocol.'''

# Import required Python modules.
import time
import re

# Import required libnuclix modules.
from libnuclix import event
from libnuclix import var
from libnuclix import server
from libnuclix import logger

uses_uid = False

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

    global uses_uid

    numeric = var.conf.get('uplink', 'numeric')[0]

    if not numeric:
        conn.push('PASS %s :TS' % conn.server['password'])
    else:
        uses_uid = True
        conn.push('PASS %s TS 6 :%s' % (conn.server['password'], numeric))

    conn.push('CAPAB :QS EX IE KLN UNKLN ENCAP TB SERVICES EUID EOPMOD MLOCK')
    conn.push('SERVER %s 1 :%s' % (conn.server['services_name'], conn.server['services_desc']))
    conn.push('SVINFO %d 3 0 :%d' % (6 if uses_uid else 5, time.time()))

def m_ping(conn, parv):
    '''Reply to PING's.'''

    global uses_uid

    conn.push(':%s PONG %s %s' % (conn.server['numeric'] if uses_uid else conn.server['services_server'], conn.server['services_server'], parv[0]))

def m_pong(conn, parv):
    '''Reply to PONG's.'''

    if not parv[0]:
        return

    if parv[0] not in var.servers:
        return

    logger.info('m_pong(): bursting to %s (%d user%s)' % (parv[0], var.servers[parv[0]]['users'], 's' if var.servers[parv[0]]['users'] != 1 else ''))

    if conn.server['actual'] == parv[0]:
        return

def m_server(conn, parv):
    '''Handle new servers.'''

    logger.info('m_server(): new server: %s' % parv[0])

def protocol_init():
    '''Protocol entry point.'''

    protocol.attach('PING', m_ping)
    protocol.attach('PONG', m_pong)
    protocol.attach('SERVER', m_server)

def protocol_fini():
    '''Protocol exit point.'''

    protocol.detach('PING', m_ping)
    protocol.detach('PONG', m_pong)
    protocol.detach('SERVER', m_server)
