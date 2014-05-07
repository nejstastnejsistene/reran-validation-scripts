import re
import subprocess
from commands import getoutput


class LogcatScanner(object):

    command = 'adb logcat'.split()
    pattern = re.compile(r'^[EF]/(\w+)\(\s*(\d+)\)')

    def __init__(self, pid):
        self.scanning = False
        self.pid = pid

    def start(self, reran_process):
        assert not self.scanning, 'Already scanning!'
        self.scanning = True
        getoutput('adb shell logcat -c') # Clear the logcat.
        self.p = subprocess.Popen(self.command, stdout=subprocess.PIPE)
        while self.scanning:
            line = self.p.stdout.readline()
            m = self.pattern.match(line)
            if m is None:
                continue
            tag, pid = m.groups()
            if tag == 'AndroidRuntime' and int(pid) == self.pid:
                print line
                reran_process.terminate()
                self.stop()
        self.p.terminate()

    def stop(self):
        self.scanning = False


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

    # Kill the package if it's running.
    for pid in get_pids(package):
        #print 'Killing PID', pid
        getoutput('adb shell su -c kill -9 {}'.format(pid))

    # Start the app.
    getoutput('adb shell am start {}'.format(package))
    time.sleep(5)

    #print 'Translating {}'.format(trace)
    getoutput('java Translate {} translated.txt'.format(trace))

    #print 'Copying trace to device'
    getoutput('adb push translated.txt /data/local/.')

    # Get the pid for the newly started app.
    pid = next(get_pids(package))

    #print 'Scanning for PID {}'.format(pid)
    scanner = LogcatScanner(pid)

    #print 'Replaying the trace'
    cmd = 'adb shell /data/local/replay /data/local/translated.txt'.split()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    threading.Thread(target=scanner.start, args=(p,)).start()
    p.wait()
