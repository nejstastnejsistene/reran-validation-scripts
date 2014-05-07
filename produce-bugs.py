from commands import getoutput

def get_pid(package):
    lines = getoutput('adb shell ps | grep {}'.format(package)).split('\n')
    if len(lines) > 1:
        raise Exception, 'More than one process for {}'.format(package)
    try:
        return int(lines[0].split()[1])
    except:
        raise Exception, 'Unable to find pid for {}'.format(package)

if __name__ == '__main__':
    print `get_pid('com.nerdyoctopus.gamedots')`
