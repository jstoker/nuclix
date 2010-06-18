#!/usr/bin/env python
# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''Main program. This is a caller to other functions in the core and some other basic routines.'''

# Import required Python modules.
import getopt, os, signal, sys

# Import required libnuclix modules.
from libnuclix import var, logger, socket, module, conf

def print_cla_help(stderr):
    '''Output command line options and their meanings.'''

    conf_str = '-c (--config) <config>: Specify the configuration file to use.'
    help_str = '-h (--help): Output this message.'
    nofork_str = '-n (--nofork): Do not fork into the background (will output log messages)'

    if stderr:
        sys.stderr.write(conf_str.append('\n'))
        sys.stderr.write(help_str.append('\n'))
        sys.stderr.write(nofork_str.append('\n'))
    else:
        print conf_str
        print help_str
        print nofork_str

def main(argv):
    '''Our entry point.'''

    # Are we root?
    if os.geteuid() == 0:
        sys.stderr.write('nuclix: will not run under root for security purposes\n')
        sys.exit(0)

    # Parse command line options and parameter list.
    try:
        opts, args = getopt.getopt(argv, 'c:hn', ['config=', 'help', 'nofork'])
    except getopt.GetoptError, err:
        print '%s\n' % err
        print_cla_help(True)
        sys.exit(os.EX_USAGE)

    for opt, arg in opts:
        if opt in ('-c', '--config'):
            var.config_file = arg
        elif opt in ('-h', '--help'):
            print_cla_help(False)
            sys.exit(os.EX_OK)
        elif opt in ('-n', '--nofork'):
            var.fork = False

    # Attach signals to handlers.
    signal.signal(signal.SIGHUP, on_sighup)
    signal.signal(signal.SIGINT, on_sigint)
    signal.signal(signal.SIGTERM, on_sigterm)
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
    signal.signal(signal.SIGALRM, signal.SIG_IGN)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    signal.signal(signal.SIGWINCH, signal.SIG_IGN)
    signal.signal(signal.SIGTTIN, signal.SIG_IGN)
    signal.signal(signal.SIGTTOU, signal.SIG_IGN)
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)

    print 'nuclix: version %s' % var.version

    # Initialize the configuration parser.
    try:
        var.conf = conf.ConfigParser(var.config_file)
    except conf.GeneralException, err:
        sys.stderr.write('nuclix: configuration error for %s: %s\n' % (var.config_file, err))
        sys.exit(os.EX_CONFIG)

    # Check to see if we are already running.
    try:
        pid_file = open(var.conf.get('options', 'pidfile')[0], 'w')

        try:
            pid = pid_file.read()
            
            if pid:
                pid = int(pid)

                try:
                    os.kill(pid, 0)
                except OSError:
                    pass

                sys.stderr.write('nuclix: an instance is already running\n')
                sys.exit(os.EX_SOFTWARE)
        finally:
            pid_file.close()
    except IOError:
        pass

    # Fork into the background.
    if var.fork:
        try:
            pid = os.fork()
        except OSError, e:
            return (e.errno, e.strerror)

        # This is the child process.
        if pid == 0:
            os.setsid()

            # Now the child fork()'s a child in order to prevent acquisition
            # of a controlling terminal.
            try:
                pid = os.fork()
            except OSError, e:
                return (e.errno, e.strerror)

            # This is the second child process.
            if pid == 0:
                os.chdir(os.getcwd())
                os.umask(0)

            # This is the first child.
            else:
                print 'nuclix: pid', pid
                print 'nuclix: running in background mode from', os.getcwd()
                os._exit(0)
        else:
            os._exit(0)

        # Try to write the PID file.
        try:
            pid_file = open(var.conf.get('options', 'pidfile')[0], 'w')
            pid_file.write(str(os.getpid()))
            pid_file.close()
        except IOError, e:
            sys.stderr.write('nuclix: unable to write pid file: %s\n' % os.strerror(e.args[0]))
            sys.exit(os.EX_SOFTWARE)

        # Try to close all open file descriptors.
        # If we cant find the max number, just close the first 256.
        try:
            maxfd = os.sysconf('SC_OPEN_MAX')
        except (AttributeError, ValueError):
            maxfd = 256

        for fd in range(0, maxfd):
            try:
                os.close(fd)
            except OSError:
                pass

        # Redirect the standard file descriptors to /dev/null.
        os.open('/dev/null', os.O_RDONLY)
        os.open('/dev/null', os.O_RDWR)
        os.open('/dev/null', os.O_RDWR)
    else:
        print 'nuclix: pid', os.getpid()
        print 'nuclix: running in foregroud mode from', os.getcwd()

    # Initialize the logger.
    logger.init()

    # Load all modules listed in the configuration.
    module.load_all_from_conf()

if __name__ == '__main__':  
    main(sys.argv[1:])
