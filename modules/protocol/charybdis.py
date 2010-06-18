# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''Charybdis IRCd protocol.'''

# Import required Python module.
import time

# Import required libnuclix modules.
from libnuclix import event
from libnuclix import var

uses_uid = False

def negotiate_link(conn):
    '''Send the linking data.'''

    global uses_uid

    numeric = var.conf.get('uplink', 'numeric')[0]

    if not numeric:
        conn.sendq.push('PASS %s :TS' % conn.server['password'])
    else:
        uses_uid = True
        conn.sendq.push('PASS %s TS 6 :%s' % (conn.server['password'], numeric))

    conn.sendq.push('CAPAB :QS EX IE KLN UNKLN ENCAP TB SERVICES EUID EOPMOD MLOCK')
    conn.sendq.push('SERVER %s 1 :%s' % (conn.server['services_name'], conn.server['services_desc']))
    conn.sendq.push('SVINFO %d 3 0 :%d' % ('6' if uses_uid else '5', time.time()))

def on_socket_read(conn, data):
    '''Read data read from the connection.'''

    pass

def module_init():
    '''Module entry point.'''

    event.attach('OnRawSocketRead', on_socket_read)

def module_fini():
    '''Module exit point.'''

    event.detach('OnRawSocketRead', on_socket_read)
