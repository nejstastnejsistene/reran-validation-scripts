#!/bin/sh

partition_events () {
    export input_file=$1
    python << EOF
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

input_file = open('$input_file')

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
                fmt = 'touch action: duration={:f}, num_coords={}, coords={}'
                print fmt.format(duration, len(coords), coords)
                events = []
                coords = []

            was_finger_down = finger_down

        # Append the current coordinates to the list.
        else:
            coords.append((x, y))


    else:
         raise Exception, 'unrecognized event: {}'.format(event)
EOF
}

expand_description () {
    export description=$1
    python << EOF
import os, sys, re
with open(os.environ['description']) as f:
    for line in f.read().split('\n'):
        if 'typed' in line.lower():
            try:
                for ch in re.search(r'"(.*)"', line).group(1):
                    print 'I touched the "{}" button on the keyboard.'.format(ch)
            except:
                print >> sys.stderr, '\nError: unable to find delimited string. Don\'t forget to add double quotes for typed events'
                sys.exit(1)
        elif line:
            print line
EOF
}

app=$1
if [ -z $app ]; then
    echo usage: $0 \<app name\>
    exit 1
fi

for lastname in `ls`; do

    # Skip non-directories.
    if [ ! -d $lastname ]; then
        continue
    fi

    # Make sure the app exists.
    if [ ! -d "$lastname/$app" ]; then
        echo \"$lastname/$app\" does not exist
        continue
    fi

    # Clear any old data before writing the new data.
    rm -f "$app-records.txt" "$app-description.txt"

    # Iterate through each scenario.
    for scenario in `ls "$lastname/$app"`; do

        # For each record, concatentate its events and descriptions.
        for record in `ls "$lastname/$app/$scenario"/record*.log`; do
            partition_events $record >> "$app-records.txt"
            expand_description "$lastname/$app/$scenario/description.txt" >> "$app-desciption.txt"
        done
    done
done

