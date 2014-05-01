import sys

def method_to_logcat_fmt(method):
    return method[:method.index('(')].strip().replace('/', '.')

with open(sys.argv[1]) as f:
    for line in f:
        _, _, method = line.strip().split(',', 2)
        if '#' in method:
            for meth in reversed(method.split('#')):
                print method_to_logcat_fmt(meth)
        else:
            print method_to_logcat_fmt(method)
