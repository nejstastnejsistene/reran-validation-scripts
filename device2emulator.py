#!/usr/bin/env python

import re
import sys
#from evdev.ecodes import *

EV_SYN = 0
EV_KEY = 1
EV_ABS = 3
ABS_X = 0
ABS_Y = 1
ABS_MT_POSITION_X = 53
ABS_MT_POSITION_Y = 54
ABS_MT_TRACKING_ID = 57
SYN_REPORT = 0
BTN_TOUCH = 330

pattern = re.compile(
        r'\[\s*(\d*\.\d*)\] /dev/input/event(\d): ' \
        r'([0-9a-f]{4}) ([0-9a-f]{4}) ([0-9a-f]{8})')

input_file = open(sys.argv[1])

x, y = 0, 0
was_finger_down = False
finger_down = False
events = []
coords = []

def translate_event(time, device, type, code, value):
    if code == ABS_MT_POSITION_X:
        return time, device, type, ABS_X, int(value / (1343.0/1200.0))
    elif code == ABS_MT_POSITION_Y:
        return time, device, type, ABS_Y, int(value / (2239.0/1920.0))
    elif code == ABS_MT_TRACKING_ID:
        if value == 0xffffffff:
            return time, device, EV_KEY, BTN_TOUCH, 0
        else:
            return time, device, EV_KEY, BTN_TOUCH, 1
    elif code == SYN_REPORT:
        return time, device, type, code, value

    # Skip events that don't have a corresponding event,
    # such as ABS_MT_PRESSURE.


def print_event(event):
    if event is not None:
        time, device, type, code, value = event
        print '[{:15.6f}] /dev/input/event{}:'.format(time, device),
        print '{:04x} {:04x} {:08x}'.format(type, code, value)


for line in input_file:
    if line[0] != '[':
        continue
    time, device, type, code, value = re.match(pattern, line).groups()
    time = float(time)
    device = int(device)
    type = int(type, 16)
    code = int(code, 16)
    value = int(value, 16)
    event = time, device, type, code, value
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
            print fmt.format(duration, device, code)
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
                i = 0
                while i < len(events):
                    e = events[i]
                    if e[3] == ABS_MT_TRACKING_ID and e[4] != 0xffffffff:
                        e1 = events[i+1]
                        e2 = events[i+2]
                        if e1[3] in (ABS_MT_POSITION_X, ABS_MT_POSITION_Y):
                            print_event(translate_event(*((e[0],)+e1[1:])))
                        if e2[3] in (ABS_MT_POSITION_X, ABS_MT_POSITION_Y):
                            print_event(translate_event(*((e[0],)+e2[1:])))
                    print_event(translate_event(*e))
                    i += 1
                events = []
                coords = []

            was_finger_down = finger_down

        # Append the current coordinates to the list.
        else:
            coords.append((x, y))


    else:
         raise Exception, 'unrecognized event: {}'.format(event)
