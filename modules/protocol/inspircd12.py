# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''InspIRCd protocol.'''

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

uses_uid = True
numeric = var.conf.get('uplink', 'numeric')[0]

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
    '''Send the linking data. noop in inspircd12'''
    pass

    #numeric = var.conf.get('uplink', 'numeric')[0]

    #conn.push('SERVER %s 1 :%s' % (conn.server['services_name'], conn.server['services_desc']))

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

    if command == 'CAPAB':
        m_capab(conn, parv)

    if command == 'PING':
        m_ping(conn, parv)

    if command == 'PONG':
        m_pong(conn, parv)

    if command == 'SERVER':
        m_server(conn, parv)

    if command == 'FJOIN':
        m_fjoin(conn, parv)

    if command == 'SQUIT':
        m_squit(conn, parv)

    if command == 'UID':
        m_uid(conn, parv)

def m_capab(conn, parv):
    if parv[0] == 'END':
        conn.push('SERVER %s %s 0 %s :%s' % (conn.server['services_name'], conn.server['password'], numeric, conn.server['services_desc']))

def m_server(conn, parv):
    '''Handle new servers.'''

    global uses_uid

    # SERVER zeus.jcs.me.uk iliketurtles 0 001 :zeus.jcs.me.uk inspircd
    logger.debug('m_server(): new server: %s' % parv[0])

    # need to make sure we only do this upon connect, and not upon other servers.
    conn.push(':%s BURST %d' % (numeric, time.time()))
    conn.push(':%s VERSION :nuclix v%s -- A minimalistic IRC service package.' % (numeric, var.version))#time.time())

    conn.push(':%s ENDBURST' % numeric)#time.time())

    #server.add(parv[0], parv[1], None, parv[3])


def m_squit(conn, parv):
    '''Handle server leavings.'''

    logger.info('m_squit(): server %s leaving from %s' % (parv[0], parv[1])) # parv[1] == the reason.
    server.delete(parv[0])

def m_fjoin(conn, parv):
    '''Channel syncing.'''
    
    # :001 FJOIN #spartairc 1276970839 +nt :o,001AAAAAA v,001AAAAAB
    # 
    # XXX: Since the regex doesn't get the information in the way we would expect,
    # we have to do this. Somebody please make an inspircd protocol regex? Thanks.o

    sparv = parv[1].split(' ')
    chan = parv[0]
    ts = sparv[0]
    channel.add(chan, ts)

def m_ping(conn, parv):
    '''Reply to PING's.'''

    global uses_uid

    numeric = var.conf.get('uplink', 'numeric')[0]

    conn.push(':%s PONG %s %s' % (numeric, parv[1], parv[0]))

def m_pong(conn, parv):
    '''Reply to PONG's.'''

    if not parv[0]:
        return

    if parv[0] not in var.servers:
        return

    logger.info('m_pong(): bursting to %s (%d user%s)' % (parv[0], var.servers[parv[0]]['users'], 's' if var.servers[parv[0]]['users'] != 1 else ''))

    if conn.server['actual'] == parv[0]:
        return

def m_uid(conn, parv):
    '''User connected.'''

    print parv

    if parv >= 9:
        logger.debug('m_uid(): user connected: %s' % parv[0])

def protocol_init():
    '''Protocol entry point.'''

    pass

def protocol_fini():
    '''Protocol exit point.'''

    pass
