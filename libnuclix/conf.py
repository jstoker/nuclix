# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE

'''Configuration parser.'''

# Import required libnuclix module.
import logger

class ConfigBlock(object):
    def __init__(self, label, values={}):
        self.label = label
        self.var = {}

        # Copy over any values given during initialization.
        for key in values:
            self.var[key] = values[key]

    def add(self, name, value):
        self.var[name] = value

    def get(self, name, defval=None):
        if defval:
            if not self.var.get(name, defval):
                raise VariableNotFound('%s:%s not found.' % (name, defval))
        else:
            return self.vars.get(name, None)

class BlockNotFound(Exception):
    '''Block not found.'''

    def __init__(self, err):
        Exception.__init__(self, err)
        self.__err = err

        logger.error('conf.BlockNotFound(): %s' % self.__err)

    def __str__(self):
        return self.__err

class VariableNotFound(Exception):
    '''Variable not found.'''

    def __init__(self, err):
        Exception.__init__(self, err)
        self.__err = err

        logger.error('conf.VariableNotFound(): %s' % self.__err)

    def __str__(self):
        return self.__err

class GeneralError(Exception):
    '''General error.'''

    def __init__(self, err):
        Exception.__init__(self, err)
        self.__err = err

        logger.error('conf.GeneralError(): %s' % self.__err)

    def __str__(self):
        return self.__err

class ConfigParser:
    '''Parse configuration files.'''

    def __init__(self, name):
        self.name = name
        self.parse()

    def rehash(self, on_sighup):
        '''Rehash configuration and change nuclix to fit the new conditions.'''

        logger.info('conf.ConfigParser(): rehashing configuration %s' % 'due to SIGHUP' if on_sighup else '')

        # Make a copy of the old data to compare it to the new data.
        self.parse()

    def parse(self):
        '''Parse our file, and put the data into a dictionary.'''

        self.line_number = 0

        # Attempt to open the file.
        try:
            conf_file = open(self.file, 'r')
        except IOError, e:
            raise GeneralError('Error opening configuration file %s: %s' % (self.file, os.strerror(e.args[0]))

        # Parse.
        self.blocks = []

        for line in conf_file.xreadlines():
            for cno, c in enumerate(line):
                if c == '\n':
                    # Increment the line number.
                    self.line_number += 1

                if c == '#': # Comment until EOL.
                    break

                if c == ':': # Block label.
                    label = line[:cno].strip()
                    self.blocks.append(ConfigBlock(label))

                if c == '=': # Variable.
                    if not self.blocks: # Skip this line, as no block label was given yet.
                        break

                    varname = line[:cno].strip()
                    varval = line[cno + 1:].strip()
                    self.blocks[-1].add(varname, varval)

                    break
                    
        # Close the file handle.
        conf_file.close()

    def xget(self, block, variable=None):
        '''
        Return whatever is in block:variable. If 'variable' == None,
        we will iterate over multiple blocks, thus allowing us to return
        multiple values from multiple blocks.
        '''

        if block not in set(b.label for b in self.blocks):
            raise BlockNotFound("Block '%s' not found" % block)

        for i in self.blocks:
            if i.label == block:
                if variable is None: # Just get blocks by this name.
                    yield i
                else:
                    # Get a member of blocks by this name.
                    yield i.get(variable)

    def get(self, block, variable=None):
        '''
        Call our iterating generator (xget) and just store all its
        results into a list to return all at once.
        '''

        return [b for b in self.xget(block, variable)]
