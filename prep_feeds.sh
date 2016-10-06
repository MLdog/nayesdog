#!/bin/bash

feeddest=~/feeds
mddest="$feeddest/md"

basedir=$(pwd)

mkdir $feeddest
mkdir $mddest

cd $feeddest
# download all feeds with curl with 4 parallel threads
cat "$basedir/urls" | xargs -n1 -P4 curl -O

# rename
for f in $(ls $feeddest); do
    newname=$(grep -oE '<title>[^<]+</title>' $f | head -1 | sed 's/<title>\([^<]\+\)<\/title>/\1/g' | tr ' ' _)
    mv $f $newname
done
python3 "$basedir/feeds2mds.py" $feeddest $mddest
