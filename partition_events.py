import sys
from evdev.ecodes import *

lines = iter(open(sys.argv[1]))

x, y = 0, 0
was_finger_down = False
finger_down = False
coords = []
duration = 0

num_events = int(next(lines))
for event in range(num_events):
    duration += int(next(lines))
    device, type, code, value = map(int, next(lines).split(','))

    # Set x coordinate.
    if type == EV_ABS and code == ABS_X:
        x = value

    # Set y coordinate.
    elif type == EV_ABS and code == ABS_Y:
        y = value

    # Finger up/down.
    elif type == EV_KEY and code == BTN_TOUCH:
        finger_down = value

    # Seperator.
    elif type == EV_SYN and code == SYN_REPORT:
        coords.append((x, y))
        if finger_down != was_finger_down:
            if finger_down:
                coords = []
                duration = 0
            else:
                fmt = 'action: duration={}, num_coords={}'
                print fmt.format(duration / 1e9, len(coords))
            was_finger_down = finger_down

    else:
        event = type, code, value
        raise Exception, 'unrecognized event: {}'.format(event)
