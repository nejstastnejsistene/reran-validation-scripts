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

for line in input_file:
    time, device, type, code, value = re.match(pattern, line).groups()
    time = float(time.replace('-', '.'))
    device = int(device)
    type = int(type, 16)
    code = int(code, 16)
    value = int(value, 16)
    event = '{},{},{},{}'.format(device, type, code, value)
    events.append(event)
    
    # Button down.
    if type == EV_KEY:

        # If the touch screen has been toggled, let sync events
        # handle the logic.
        if code == BTN_TOUCH:
            finger_down = value

        # For any other button, print the action after the button has
        # been released.
        elif value == 0:
            print ','.join(events),
            events = []

    # Absolute coordinates from a touchscreen.
    elif type == EV_ABS:
        if code == ABS_X:
            x = value
        elif code == ABS_Y:
            y = value

    # Sync.
    elif type == EV_SYN and code == SYN_REPORT:

        # If the finger has changed:
        if finger_down != was_finger_down:

            # Restart the coordinate list.
            if finger_down:
                coords = [(x, y)]

            # If the finger is removed from the touchscreen, end the
            # action and print the events.
            else:
                print ','.join(events),
                events = []

            was_finger_down = finger_down

        # Append the current coordinates to the list.
        else:
            coords.append((x, y))


    else:
         raise Exception, 'unrecognized event: {}'.format(event)
