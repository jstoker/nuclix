# nuclix -- A minimalistic IRC service package.
# Copyright (C) 2010 Michael Rodriguez.
# Rights to this code are documented in docs/LICENSE.

'''Timer management.'''

# Import required Python modules.
import time

# Import required libnuclix modules.
import var
import event

# The lowest time when a timer must execute.
timer_min = -1

def new():
    '''Make a new timer.'''

    timer = { 'name'   : None,
              'func'   : None,
              'args'   : None,
              'freq'   : 0,
              'when'   : 0,
              'active' : False }

    return timer

def add(name, only_once, func, freq, args=None):
    '''Add a new timer to be executed every `freq` seconds.'''

    global timer_min

    timer = new()

    timer['name'] = name
    timer['func'] = func
    timer['args'] = args
    timer['freq'] = freq if not only_once else 0
    timer['when'] = (time.time() + freq)
    timer['active'] = True

    if timer['when'] < timer_min or timer_min == -1:
        timer_min = timer['when']

    var.timers.append(timer)
    event.dispatch('OnAddTimer', timer)

def delete(func, args=None):
    '''Delete all timers with matching `func` and `args`.'''

    var.timers = [timer for timer in var.timers if timer['func'] != func and timer['args'] != args]
    event.dispatch('OnTimerDelete', func, args)

def next_run():
    '''Return the time the next timer has to be executed.'''

    global timer_min

    for timer in var.timers:
        if timer['when'] < timer_min or timer_min == -1:
            timer_min = timer['when']

    return timer_min

def run():
    '''Execute all timers that need to be executed.'''

    global timer_min

    for timer in var.timers:
        if timer['when'] <= time.time():
            timer['func'](timer['args'])
            timer_min = -1

            event.dispatch('OnTimerCallFunction', timer['func'], timer['args'])

        # If it's scheduled more than once updated its `when`.
        if timer['freq']:
            timer['when'] = (time.time() + timer['freq'])

            if timer['when'] < timer_min or timer_min == -1:
                timer_min = timer['when']

        # Otherwise mark it as inactive.
        else:
            timer['active'] = False

    # Delete any timers that aren't useful anymore.
    var.timers = [timer for timer in var.timers if timer['active']]
