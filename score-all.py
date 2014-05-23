#!/usr/bin/env python

import sys
import os
import glob
import fnmatch

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

def method_to_logcat_fmt(method):
    if '(' in method:
        method = method[:method.index('(')]
    return method.strip().replace('/', '.')

def sanitize_scenario(filename):
    with open(filename) as f:
        for line in f:
            try:
                _, _, method = line.strip().split(',', 2)
            except:
                print >>sys.stderr, filename
                print >>sys.stderr, line
            if '#' in method:
                for meth in reversed(method.split('#')):
                    yield method_to_logcat_fmt(meth)
            else:
                yield method_to_logcat_fmt(method)

def read_logcat(filename):
    with open(filename) as f:
        return f.read().split()

def compare_trace(scenario_filename, logcat_filename):
    scenario = list(sanitize_scenario(scenario_filename))
    logcat = read_logcat(logcat_filename)
    seq = lcs(scenario, logcat)
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

    return logcat_filename, get_description(scenario_filename), \
            scenario_filename, len(seq), norm, 'produce-bug?'

def logcats(app):
    return sorted(glob.glob('reran/results/logcats/' + app + '/*_final.txt'))

def scenarios(app):
    for root, dirnames, filenames in os.walk('reran/results/' + app):
        for filename in fnmatch.filter(filenames, '*.at2'):
            yield os.path.join(root, filename)

def split_directories(path):
    folders = []
    while True:
        path,folder = os.path.split(path)
        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)
            break
    return list(reversed(folders))

def get_description(scenario):
    path = app, name, scenario = split_directories(scenario)[2:-1]
    desc_path = os.path.join('reran', 'repository', name, app, scenario, 'description.txt')
    assert os.path.exists(desc_path), desc_path
    return desc_path

def compare_all(app):
    for logcat in logcats(app):
        for scenario in scenarios(app):
            yield compare_trace(scenario, logcat)

if __name__ == '__main__':
    tuples = compare_all(sys.argv[1])
    for x in sorted(tuples, key=lambda x: (x[0], 1-x[-2])):
        print ', '.join(map(str, x))

