import re
import sys
from evdev.ecodes import *

pattern = re.compile(
        r'(\d*\-\d*): /dev/input/event(\d): ' \
        r'([0-9a-f]{4}) ([0-9a-f]{4}) ([0-9a-f]{8})')

input_file = open(sys.argv[1])

x, y = 0, 0
was_finger_down = False
finger_down = False
events = []
coords = []
start_time = 0

for event in input_file:
    time, device, type, code, value = re.match(pattern, event).groups()
    time = float(time.replace('-', '.'))
    device = int(device)
    type = int(type, 16)
    code = int(code, 16)
    value = int(value, 16)
    
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
                start_time = time
            else:
                fmt = 'action: duration={}, num_coords={}'
                print fmt.format(time - start_time, len(coords))
            was_finger_down = finger_down

    else:
        event = type, code, value
        raise Exception, 'unrecognized event: {}'.format(event)
