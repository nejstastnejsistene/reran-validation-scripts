def lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = \
                    max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = []
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert a[x-1] == b[y-1]
            result.insert(0, a[x-1])
            x -= 1
            y -= 1
    return result


import sys
from commands import getoutput
scenario = getoutput('python sanitize-traces.py "{0}" | uniq'.format(sys.argv[1])).split()
stack_trace = open(sys.argv[2]).read().split()

seq = lcs(scenario, stack_trace)
if seq:
    first_index = last_index = scenario.index(seq[0])
    for item in seq[1:]:
        last_index = scenario.index(item, last_index)
    if len(seq) == 1:
        norm = 1.0
    else:
        norm = len(seq) / float(last_index - first_index)
else:
    norm = 0.0

print '<{0}, {1}, {2}, {3}>'.format(sys.argv[1], sys.argv[2], len(seq), norm)
