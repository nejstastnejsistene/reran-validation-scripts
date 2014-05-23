#!/usr/bin/env python

import sys
import select
import re
import subprocess
from commands import getoutput


scanning = False

def scan_logcat(target_pid, reran_process, q):
    global scanning
    scanning = True
    pattern = re.compile(r'^[EF]/(\w+)\(\s*(\d+)\)')
    getoutput('adb shell logcat -c') # Clear the logcat.
    p = subprocess.Popen('adb logcat'.split(), stdout=subprocess.PIPE)
    while scanning:
        rlist, _, _ = select.select([p.stdout], [], [], 0.1)
        if not rlist:
            continue
        line = p.stdout.readline()
        m = pattern.match(line)
        if m is None:
            continue
        tag, pid = m.groups()
        if tag == 'AndroidRuntime' and int(pid) == target_pid:
            #print >>sys.stderr, line
            q.put(line)
            try:
                reran_process.terminate()
                reran_process.kill()
            finally:
                break
    p.terminate()

def get_pids(package):
    lines = getoutput("adb shell ps | grep {} | awk '{{print $2}}'".format(package))
    for pid in lines.split():
        yield int(pid)


if __name__ == '__main__':
    import sys, time, threading
    if len(sys.argv) != 3:
        print >>sys.stderr, 'usage: {} <package> <trace>'.format(sys.argv[0])

    package = sys.argv[1]
    trace = sys.argv[2]

    # (Re)start the app.
    getoutput('adb shell am force-stop {}'.format(package))
    time.sleep(1)
    getoutput('adb shell am start {}/.ui.MainActivity'.format(package))
    time.sleep(1)

    getoutput('java Translate {} translated.txt'.format(trace))
    getoutput('adb push translated.txt /data/local/.')

    start = time.time()

    cmd = 'adb shell /data/local/replay /data/local/translated.txt'.split()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    from Queue import Queue
    q = Queue()

    # Get the pid for the newly started app.
    pid = next(get_pids(package))
    threading.Thread(target=scan_logcat, args=(pid, p, q)).start()

    p.wait()
    end = time.time()
    time.sleep(1)

    print '{},{}'.format(str(not q.empty()).lower(), end - start)

    scanning = False
