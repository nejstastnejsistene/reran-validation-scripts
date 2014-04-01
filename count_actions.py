#!/usr/bin/env python

import sys
import re
from commands import getoutput

if len(sys.argv) != 3:
    print >> sys.stderr, 'usage: {} <scenario> <events>'.format(__file__)

with open(sys.argv[1]) as f:
    scenario = filter(None, f)

events = getoutput('./partition_events.py {}'.format(sys.argv[2]))
events = filter(None, events.split('\n'))

max_len = max(map(len, scenario)) + 2

s = iter(scenario)
e = iter(events)
while True:
    try:
        line = next(s).strip()
    except StopIteration:
        # Break when we run out of lines in the scenario.
        break
    try:
        if 'typed' in line.lower():
            print line
            try:
                in_quotes = re.search(r'"(.*)"', line).group(1)
                for i in in_quotes:
                    print (' '*4 + i).ljust(max_len, '.'), next(e)
            except:
                print >> sys.stderr, '\nError: unable to find delimited string. Don\'t forget to add double quotes for typed events'
                sys.exit(1)
        else:
            print line.ljust(max_len, '.'), next(e)
    except StopIteration:
        print >> sys.stderr, '\nError: Too few events!'
        sys.exit(1)

# Make sure we are also out of events.
# This means there are the same number of scenarios and events.
try:
    next(e)
    print >> sys.stderr, '\nError: Too many events!'
    sys.exit(1)
except StopIteration:
    print '\nSuccess: It looks like they match up!'
