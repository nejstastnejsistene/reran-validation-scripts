import sys, os

data = sys.argv[1]

for line in open(data):
    trace, _, _, produce_bug, duration = line.split(', ')[-5:]
    reran, results, app, name, scenario, record = trace.split('/')
    record = record[:-4].replace('replay', 'record')
    getevents = os.path.join(reran, 'repository', name, app, scenario, record)
    assert os.path.exists(getevents), getevents
    produce_bug = produce_bug == 'true'
    duration = float(duration)
    num_events = 0
    start = None
    with open(getevents) as f:
        for x in f:
            if x.startswith('['):
                timestamp = float(x[1:x.index(']')])
                if start is None:
                    num_events += 1
                    start = timestamp
                elif produce_bug and timestamp - start > duration:
                    break
                else:
                    num_events += 1
    print '{}, {}'.format(line.strip(), num_events)
