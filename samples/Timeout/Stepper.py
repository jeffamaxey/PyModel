"""
Simple Stepper to experiment with timeouts in pmt
"""

import time

def TestAction(aname, args, modelResult):
    if aname != 'sleep':
        raise NotImplementedError(f'action not supported by stepper: {aname}')
    (seconds,) = args
    time.sleep(seconds)

def Reset():
    pass
