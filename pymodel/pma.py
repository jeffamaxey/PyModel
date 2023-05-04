#!/usr/bin/env python
"""
PyModel Analyzer - generate FSM from product model program
"""

from pymodel import Analyzer
from pymodel import AnalyzerOptions
from pymodel.ProductModelProgram import ProductModelProgram

def main():
    (options, args) = AnalyzerOptions.parse_args()
    if not args:
        AnalyzerOptions.print_help()
        exit()
    else:
        mp = ProductModelProgram(options, args)
        Analyzer.explore(mp, options.maxTransitions)
        print(
            f'{len(Analyzer.states)} states, {len(Analyzer.graph)} transitions, {len(Analyzer.accepting)} accepting states, {len(Analyzer.unsafe)} unsafe states'
        )
        mname = options.output if options.output else f'{args[0]}FSM'
        Analyzer.save(mname)

if __name__ == '__main__':
    main ()
