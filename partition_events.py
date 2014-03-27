import re
import sys
from evdev.ecodes import *

pattern = re.compile(
        r'\[\s*(\d*\.\d*)\] /dev/input/event(\d): ' \
        r'([0-9a-f]{4}) ([0-9a-f]{4}) ([0-9a-f]{8})')

input_file = open(sys.argv[1])

x, y = 0, 0
was_finger_down = False
finger_down = False
events = []
coords = []

for line in input_file:
    if line[0] != '[':
        continue
    time, device, type, code, value = re.match(pattern, line).groups()
    time = float(time)
    device = int(device)
    type = int(type, 16)
    code = int(code, 16)
    value = int(value, 16)
    event = device, type, code, value
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
            duration = time - start_time
            fmt = 'button press: duration={}, device={}, code={}'
            print fmt.format(duration, device, keys[code])
            events = []
        elif value == 1:
            start_time = time

    # Absolute coordinates from a touchscreen.
    elif type == EV_ABS:
        if code in (ABS_X, ABS_MT_POSITION_X):
            x = value
        elif code in (ABS_Y, ABS_MT_POSITION_Y):
            y = value
	elif code == ABS_MT_TRACKING_ID:
            finger_down = value != 0xffffffff 

    # Sync.
    elif type == EV_SYN and code == SYN_REPORT:

        # If the finger has changed:
        if finger_down != was_finger_down:

            # Restart the coordinate list.
            if finger_down:
                start_time = time
                coords = [(x, y)]

            # If the finger is removed from the touchscreen, end the
            # action and print the events.
            else:
                duration = time - start_time
                fmt = 'touch action: duration={}, coords={}'
                print fmt.format(duration, coords)
                events = []
                coords = []

            was_finger_down = finger_down

        # Append the current coordinates to the list.
        else:
            coords.append((x, y))


    else:
         raise Exception, 'unrecognized event: {}'.format(event)
