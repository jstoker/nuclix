# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''Module management.'''

# Import required Python function.
from imp import load_source

# Import required libnuclix modules.
import var
import logger
import event
import conf

def load(module):
    '''Load a module.'''

    mod = None

    try:
        mod = load_source(module, module)
    except ImportError, e:
        logger.error('module.load(): unable to load module %s: %s' % (module, e))
        return

    # Check to make sure the module has init/fini functions.
    if not hasattr(mod, 'module_init'):
        logger.error('module.load(): unable to use module %s: no entry point has been defined' % mod.__name__)
        return

    if not hasattr(mod, 'module_fini'):
        logger.error('module.load(): unable to use module %s: no exit point has been defiend' % mod.__name__)
        return

    mod.module_init()
    logger.info('module.load(): module %s loaded' % mod.__name__)

    # Add the module to the loaded modules list.
    var.modules_loaded.append(mod)
    event.dispatch('OnModuleLoad', mod)

def unload(module):
    '''Unload a module.'''

    if module not in var.modules_loaded:
        logger.warning('module.unload(): %s is not in the loaded modules list' % module)
        return

    module.module_fini()

    # Remove the module from the loaded modules list.
    var.modules_loaded.remove(module)
    event.dispatch('OnModuleUnload', module)

def find(name):
    '''Find a module within the loaded modules list.'''

    for i in var.modules_loaded:
        if i.__name__ == name:
            return True

    return False

def unload_all():
    '''Unload all loaded modules.'''

    for i in var.modules_loaded:
        unload(i)

    event.dispatch('OnModuleUnloadAll')

def load_all_from_conf():
    '''Load all modules listed in configuration.'''

    try:
        for i in var.conf.get('module'):
            name = i.get('name')

            if name:
                load(name)
    except:
        pass # Means they dont want modules loaded.

    event.dispatch('OnModuleLoadAllFromConf')
