# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE

'''Uplink handling.'''

# Import required Python modules.
import asyncore
import traceback
import os
import re
import socket

# Import required Python functions.
from collections import deque
from time import time

# Import required libnuclix modules.
import logger
import var
import timer
import protocol

# Import required libnuclix function.
from libnuclix import shutdown

class UplinkConnection(asyncore.dispatcher):
    '''Provide an event based IRC connection.'''

    def __init__(self, server):
        asyncore.dispatcher.__init__(self)

        self.server = server
        self.holdline = None
        self.last_recv = time()
        self.pinged = False

        self.sendq = deque()
        self.recvq = deque()

    def writeable(self):
        '''See if we should write data.'''

        return len(self.sendq) > 0

    def handle_read(self):
        '''Handle data read from the socket.'''

        data = self.recv(8192)
        self.last_recv = time.time()

        # This means the connection was closed.
        # handle_close() takes care of all of this.
        if not data:
            return

        datalines = data.split('\r\n')

        # Get rid of the empty element at the end.
        if not datalines[-1]:
            datalines.pop()

        # Check to see if we got part of a line previously.
        # If we did, prepend it to the first line this time.
        if self.holdline:
            datalines[0] = self.holdline + datalines[0]
            self.holdline = None

        # Check to make sure we got a full line at the end.
        if not data.endswith('\r\n'):
            self.holdline = datalines[-1]
            datalines.pop()

        # Add this jazz to the recvq.
        self.recvq.extend([line for line in datalines])

        # Dispatch it.
        event.dispatch('OnRawSocketRead', datalines)

    def handle_write(self):
        '''Write the first line in the sendq to the socket.'''

        # Grab the first line from the sendq.
        line = self.sendq[-1] + '\r\n'

        # Try to send it.
        num_sent = self.send(line)

        # If it didn't all send we have to work this out.
        if num_sent == len(line):
            event.dispatch('OnRawSocketWrite', self, line)
            logger.debug('conn.UplinkConnection().handle_write(): %s <- %s' % (self.server['address'], self.sendq.pop()))
        else:
            logger.warning('conn.UplinkConnection().handle_write(): incomplete write (%d byte%s written instead of %d)' % (num_sent, 's' if num_sent != 1 else '', len(line)))
            self.sendq[-1] = self.sendq[-1][num_sent:]

    def handle_connect(self):
        '''Log into the IRC server.'''

        logger.info('conn.UplinkConnection().handle_connect(): connection established')

        self.server['connected'] = True
        protocol.negotiate.link(self)

    def handle_close(self):
        '''Handle connection closings.'''

        asyncore.dispatcher.close(self)

        logger.info('conn.UplinkConnection().handle_close(): connection lost')
        self.server['connected'] = False

        if self.server['recontime']:
            logger.info('conn.UplinkConnection().handle_close(): reconnecting in %d second%s' % (self.server['recontime'], 's' if self.server['recontime'] != 1 else ''))
            timer.add('uplink.reconnect', True, connect, self.server['recontime'], self.server)

            event.dispatch('OnReconnect', self.server)
        else:
            # Log it and exit.
            logger.info('conn.UplinkConnection().handle_close(): not reconnecting to the uplink, will exit now')
            shutdown(os.EX_SOFTWARE, 'no reconnection to uplink, therefore we dont need to hang around')

    def handle_error(self):
        '''Record a normal traceback and exit.'''

        logger.critical('conn.UplinkConnection().handle_error(): asyncore failure (BUG)')

        try:
            traceback_file = var.conf.get('options', 'traceback_file')[0]
        except var.conf.VariableNotFound:
            raise

        try:
            tracefile = open(traceback_file, 'w')
            traceback.print_exc(file=tracefile)
            tracefile.close()

            # Print one to the screen if we're not forked.
            if not var.fork:
                traceback.print_exc()
        except:
            raise

        shutdown(os.EX_SOFTWARE, 'asyncore failure')

def init():
    '''Connect to the uplink.'''

    serv = { 'id'        : None,
             'address'   : None,
             'password'  : None,
             'vhost'     : None,
             'actual'    : None,
             'port'      : 0,
             'recontime' : 0,
             'connected' : False }

    try:
        serv['id'] = var.conf.get('uplink', 'id')[0]
        serv['address'] = var.conf.get('uplink', 'address')[0]
        serv['password'] = var.conf.get('uplink', 'password')[0]
        serv['vhost'] = var.conf.get('uplink', 'vhost')[0]
        serv['actual'] = var.conf.get('uplink', 'actual')[0]
        serv['port'] = int(var.conf.get('uplink', 'port')[0])

        if var.conf.get('uplink', 'recontime')[0]:
            serv['recontime'] = int(var.conf.get('uplink', 'recontime')[0])
    except (var.conf.BlockNotFound, var.conf.VariableNotFound):
        shutdown(os.EX_CONFIG, 'uplink directives missing')

    event.dispatch('OnUplinkRecognization', serv)

    logger.info('conn.init(): connecting to %s (%s:%d)' % (serv['id'], serv['address'], serv['port']))
    uconn = UplinkConnection(serv)

    event.dispatch('OnPreConnect', serv)

    # This step is low-level to permit IPv6.
    af, type, proto, canon, sa = socket.getaddrinfo(serv['address'], serv['port'], 0, 1)[0]
    uconn.create_socket(af, type)

    # If there's a vhost, bind to it.
    if serv['vhost']:
        uconn.bind((serv['vhost'], 0))

    # Now connect to the uplink.
    uconn.connect(sa)
