#!/bin/sh

for logcat in *_final.txt; do
    for scenario in `find traces -name '*.at'`; do
        python score-traces.py $scenario $logcat
    done
done
