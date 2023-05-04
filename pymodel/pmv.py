#!/usr/bin/env python
"""
PyModel Viewer - call pma, pmg, dot.
Collect all the command line options and redistribute them to each program
"""

import os
from pymodel import ViewerOptions

# an option in a singleton tuple means there might be a list of such options
# use tuples not lists here so they can be keys in dict
pma_keys = ( ('action',), ('exclude',), 'maxTransitions', 'output' )
pmg_keys = ( 'transitionLabels', 'noStateTooltip', 'noTransitionTooltip' )

def make_opts(keys, options):
    """
    Turn options object back into a string of command line options
    """
    # special case, don't print True for boolean options --noStateTooltip etc.
    return ' '.join(
        [
            ' '.join([f'--{k[0]} {v}' for v in options.__dict__[k[0]]])
            if isinstance(k, tuple)
            else f"--{k} {options.__dict__[k] if options.__dict__[k] != True else ''}"
            for k in keys
            if options.__dict__[k[0] if isinstance(k, tuple) else k]
        ]
    )

def command(cmd):
    print(cmd) # DEBUG
    if status := os.system(cmd):
        print(f'Failed: {cmd}')

def main():
    (options, args) = ViewerOptions.parse_args()
    if not args:
        ViewerOptions.print_help()
        exit()
    else:
        basename = (
            options.__dict__['output']
            if options.__dict__['output']
            else f'{args[0]}FSM'
        )
        pma = f'pma {make_opts(pma_keys, options)} ' + ' '.join(args)
        command(pma)
        pmg = f'pmg {make_opts(pmg_keys, options)}' + f' {basename}'
        command(pmg)
        dot = 'dot -T%(type)s -o %(name)s.%(type)s %(name)s.dot' % \
            {'type': options.__dict__['fileType'], 'name': basename}
        command(dot)

if __name__ == ' __main__':
    main()
