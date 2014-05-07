#!/bin/sh

app=calculator
zipfile=reran/results/logcats/calculator/calculator_bug5.zip

dirname=`unzip -l $zipfile | head -n4 | tail -n1 | awk '{print $4}'`
unzip -qf $zipfile
if [ $? -ne 0 ]; then
    echo can\'t unzip $zipfile
    exit 1
fi

package=`grep package $dirname/AndroidManifest.xml | sed 's/.*"\(.*\)"[^"]*$/\1/'`
adb install `find $dirname -name '*.apk'` > /dev/null 2>&1

for name in `ls reran/repository`; do
    if [ -d "reran/repository/$name/$app" ]; then
        for scenario in `ls reran/repository/$name/$app`; do
            path="reran/repository/$name/$app/$scenario"
            echo -n $zipfile,$path,
            output=`./produces-bug.py $package "$path/record1.log"`
            if [ -n "$output" ]; then
                echo true
            else
                echo false
            fi
        done
    fi
done
