import re
import subprocess
from commands import getoutput


class LogcatScanner(object):

    command = 'adb logcat'.split()
    pattern = re.compile(r'^[EF]/(\w+)\(\s*(\d+)\)')

    def __init__(self, pid):
        self.scanning = False
        self.pid = pid

    def start(self):
        assert not self.scanning, 'Already scanning!'
        self.scanning = True
        getoutput('adb shell logcat -c') # Clear the logcat.
        p = subprocess.Popen(self.command, stdout=subprocess.PIPE)
        while self.scanning:
            line = p.stdout.readline()
            m = self.pattern.match(line)
            if m is None:
                continue
            tag, pid = m.groups()
            if tag == 'AndroidRuntime' and int(pid) == self.pid:
                break

    def stop(self):
        self.scanning = False


def get_pids(package):
    lines = getoutput("adb shell ps | grep {} | awk '{{print $2}}'".format(package))
    for pid in lines.split():
        yield int(pid)

if __name__ == '__main__':
    import sys, time
    package = sys.argv[1]

    # Kill the package if it's running, and the restart it.
    for pid in get_pids(package):
        print 'Killing PID', pid
        getoutput('adb shell su -c kill -9 {}'.format(pid))

    # Start the app.
    print getoutput('adb shell am start {}'.format(package))
    time.sleep(1)

    # Get the pid for the newly started app.
    pid = next(get_pids(package))

    # Scan for errors.
    print 'Scanning for PID {}'.format(pid)
    LogcatScanner(pid).start()
