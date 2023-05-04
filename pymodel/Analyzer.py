"""
Analyzer functions
"""


import sys
import os.path
from copy import deepcopy

# rebind in explore

anames = []

states = []

initial = 0 # always, keep as well as runstarts (below) for backward compat.

accepting = []
frontier = []
finished = []
deadend = []
runstarts = []
unsafe = []

graph = []

def explore(mp, maxTransitions):
    # some globals may not be needed; code only mutates collection *contents*, 
    # as in finished, deadend
    global anames, states, graph, accepting, frontier, unsafe
    anames = mp.anames
    explored = []
    fsm = []
    more_runs = True # TestSuite might have multiple runs
    while more_runs:
        initialState = mp.Current()
        frontier.append(initialState)
        states.append(initialState) # includes initial state even if no trans'ns
        iInitial = states.index(initialState) # might already be there
        runstarts.append(iInitial)
        if mp.Accepting(): # initial state might be accepting even if no trans'ns
          accepting.append(iInitial)
        if not mp.StateInvariant():
          unsafe.append(iInitial)
        while frontier:
            if len(graph) == maxTransitions:
                break
            current = frontier[0]   # head, keep in mind current might lead nowhere
            frontier = frontier[1:] # tail
            icurrent = states.index(current) # might already be there
            #print 'current %s' % current # DEBUG
            #print '   frontier %s' % frontier # DEBUG
            explored.append(current) # states we checked, some might lead nowhere
            mp.Restore(deepcopy(current)) # assign state in mp, need deepcopy here
            transitions = mp.EnabledTransitions([])
            if not transitions: # terminal state, no enabled transitions
              if icurrent in accepting:
                finished.append(icurrent)
              else:
                deadend.append(icurrent)
            # print 'current %s, transitions %s' % (current, transitions) # DEBUG
            for (aname, args, result, next, next_properties) in transitions:
          # EnabledTransitions doesn't return transitions where not statefilter
          # if next_properties['statefilter']: 
                if len(graph) < maxTransitions:
                    if next not in explored and next not in frontier:
                        # append for breadth-first, push on head for depth-first
                        frontier.append(next) # frontier contents are already copies
                    transition = (current, (aname, args, result), next)
                    if transition not in fsm:
                        fsm.append(transition)
                        if current not in states:
                            states.append(current)
                        if next not in states:
                            states.append(next) # next might never be in explored
                        # icurrent = states.index(current) # might already be there
                        inext = states.index(next) # ditto
                        graph.append((icurrent, (aname,args,result), inext)) #tuple
                        if mp.Accepting() and icurrent not in accepting:
                            accepting.append(icurrent)
                        if not mp.StateInvariant() and icurrent not in unsafe:
                            unsafe.append(icurrent)
                        if next_properties['accepting'] and inext not in accepting:
                            accepting.append(inext)
                        if not next_properties['stateinvariant'] and inext not in unsafe:
                            unsafe.append(inext)
                        # TK likewise dead states ... ?
                else: # found transition that will not be included in graph
                    frontier.insert(0,current) # not completely explored after all
                    # explored.remove(current) # not necessary
                    break
                # end if < ntransitions else ...
                # end for transitions
        # end while frontier

        # continue exploring test suite with multiple runs
        more_runs = False
        if mp.TestSuite:
            try:
                mp.Reset()
                more_runs = True
            except StopIteration: # raised by TestSuite Reset after last run
                pass # no more runs, we're done
    # end while more_runs
        

def actiondef(aname):
    return f'def {aname}(): pass'

def state(i, state):
    return f'{i} : {state},'

def initial_state(): # all FSMs
    return f'initial = {initial}'

def runstarts_states(): # initial states of test runs after the first, if any
    return f'runstarts = {runstarts}'

def accepting_states():
    return f'accepting = {accepting}'

def frontier_states():
    return f'frontier = {[states.index(s) for s in frontier]}'

def finished_states():
    return f'finished = {finished}'

def deadend_states():
    return f'deadend = {deadend}'

def unsafe_states():
    return f'unsafe = {unsafe}'

def quote_string(x): # also appears in Dot
    if isinstance(x,tuple):
        return str(x)
    else:
        return f"'{x}'" if isinstance(x, str) else f"{x}"

def transition(t):
    # return '%s' % (t,) # simple but returns quotes around action name
    current, (action, args, result), next = t
    return f'({current}, ({action}, {args}, {quote_string(result)}), {next})'

def save(name):
    with open(f"{name}.py", 'w') as f:
        f.write('\n# %s' % os.path.basename(sys.argv[0])) # echo command line ...
        f.write(' %s\n' % ' '.join([f'{arg}' for arg in sys.argv[1:]]))
        f.write('# %s states, %s transitions, %s accepting states, %s unsafe states, %s finished and %s deadend states\n' % \
                (len(states),len(graph),len(accepting),len(unsafe),len(finished),len(deadend)))
        f.write('\n# actions here are just labels, but must be symbols with __name__ attribute\n\n')
        f.writelines([ actiondef(aname)+'\n' for aname in anames ])
        f.write('\n# states, key of each state here is its number in graph etc. below\n\n')
        f.write('states = {\n')
        for i,s in enumerate(states):
            f.write('  %s\n' % state(i,s))
        f.write('}\n')
        f.write('\n# initial state, accepting states, unsafe states, frontier states, deadend states\n\n')
        f.write('%s\n' % initial_state())
        f.write('%s\n' % accepting_states())
        f.write('%s\n' % unsafe_states())
        f.write('%s\n' % frontier_states())
        f.write('%s\n' % finished_states())
        f.write('%s\n' % deadend_states())
        f.write('%s\n' % runstarts_states())
        f.write('\n# finite state machine, list of tuples: (current, (action, args, result), next)\n\n')
        f.write('graph = (\n')
        f.writelines([ '  %s,\n' % transition(t) for t in graph ])
        f.write(')\n')
