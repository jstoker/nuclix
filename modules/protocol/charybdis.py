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
from libnuclix import protocol
from libnuclix import channel

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

    if command == 'PING':
        m_ping(conn, parv)

    if command == 'PONG':
        m_pong(conn, parv)

    if command == 'SERVER':
        m_server(conn, parv)

    if command == 'SJOIN':
        m_sjoin(conn, parv)

    if command == 'SQUIT':
        m_squit(conn, parv)

    if command == 'EUID':
        m_euid(conn, parv)

def m_squit(conn, parv):
    '''Handle server leavings.'''

    logger.info('server %s leaving from %s' % (parv[0], parv[1]))
    server.delte(parv[0])

def m_sjoin(conn, parv):
    '''Channel syncing.'''
    
    # :proteus.malkier.net SJOIN 1073516550 #shrike +tn :@sycobuny @+rakaur
    #
    # XXX: Since the regex doesn't get the information in the way we would expect,
    # we have to do this. Somebody please make a charybdis protocol regex? Thanks.
    sparv = parv[1].split(' ')
    chan = sparv[0]
    ts = sparv[1]

    channel.add(chan, ts)

def m_ping(conn, parv):
    '''Reply to PING's.'''

    global uses_uid

    numeric = var.conf.get('uplink', 'numeric')[0]

    conn.push(':%s PONG %s %s' % (numeric if uses_uid else conn.server['services_name'], conn.server['services_name'], parv[0]))

def m_pong(conn, parv):
    '''Reply to PONG's.'''

    if not parv[0]:
        return

    if parv[0] not in var.servers:
        return

    logger.info('bursting to %s (%d user%s)' % (parv[0], var.servers[parv[0]]['users'], 's' if var.servers[parv[0]]['users'] != 1 else ''))

    if conn.server['actual'] == parv[0]:
        return

def m_server(conn, parv):
    '''Handle new servers.'''

    global uses_uid

    # XXX: Since the regex doesn't get the information in the way we would expect,
    # we have to do this. Somebody please make a charybdis protocol regex? Thanks.
    sparv = parv[1].split(' ')

    # SERVER salvation.sephuin.net 1 :(H) Seeking salvation.
    logger.debug('new server: %s' % parv[0])

    server.add(parv[0], sparv[0], None, sparv[2], sparv[3])

def m_euid(conn, parv):
    '''User connected.'''

    # :42X EUID dKingston 1 1276815544 +Zahloswz ~logic ov796-372.members.linode.com 97.107.140.237 42XAAAAAC li101-237.members.linode.com * :Michael Rodriguez

    # XXX: Since the regex doesn't get the information in the way we would expect,
    # we have to do this. Somebody please make a charybdis protocol regex? Thanks.
    sparv = parv[1].split(' ')

    if parv >= 11:
        logger.debug('user connected: %s' % parv[0])
        #user.add(parv[0], sparv[4], sparv[5] if sparv[8].startswith('*') else sparv[8], sparv[5], sparv[6], sparv[7], sparv[8], None, sparv[0]))

def protocol_init():
    '''Protocol entry point.'''

    pass

def protocol_fini():
    '''Protocol exit point.'''

    pass
