#!/bin/sh

DOMAIN=$( echo "$1" | awk -F/ '{print $3}')
wget --recursive \
     --continue \
     --page-requisites \
     --html-extension \
     --convert-links \
     --wait=9 \
     --limit-rate=10K \
     --restrict-file-names=windows \
     --domains $DOMAIN \
     --no-parent \
     --tries=3 \
     $1
