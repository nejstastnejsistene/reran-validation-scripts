#!/bin/bash

app=gm-dice
zipfile=reran/results/logcats/$app/"$app"_bug5.zip

dirname=`unzip -l $zipfile | head -n4 | tail -n1 | awk '{print $4}'`
if [ ! -d "$dirname" ]; then
    unzip -q $zipfile
    if [ $? -ne 0 ]; then
        echo can\'t unzip $zipfile
        exit 1
    fi
fi

package=`grep package $dirname/AndroidManifest.xml | sed 's/.*"\(.*\)"[^"]*$/\1/'`
adb uninstall "$package" > /dev/null 2>&1
adb install `find $dirname -name '*.apk'` > /dev/null 2>&1

echo $package

seen=
for name in `ls reran/repository`; do
    if [ -d "reran/repository/$name/$app" ]; then
        for scenario in `ls reran/repository/$name/$app`; do
            path="reran/repository/$name/$app/$scenario"
            for trace in `find "$path" -name 'record*.log'`; do
                if [ "$scenario" = "complicated-log" ]; then
                    if [ "`basename "$trace"`" = 'record1.log' ]; then
                        echo 'press any key when screen is sideways'
                        read -n 1 -s
                    fi
                fi
                echo -n `basename $zipfile`,$trace,
                ./produces-bug.py $package "$trace"
                if [ "$scenario" = "complicated-log" ]; then
                    if [ "`basename "$trace"`" = 'record1.log' ]; then
                        echo 'press any key when screen is upright'
                        read -n 1 -s
                    fi
                fi
            done
        done
    fi
done
