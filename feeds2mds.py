#!/usr/bin/env python3
import sys
import feedparser
import os

from doglib import feed_to_md_file

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('please call with input folder as first argument and second as output')
    else:
        inpath = sys.argv[1]
        outpath = sys.argv[2]

        infiles = list(filter(lambda s: s[0] != '.', os.listdir(inpath)))

        # convert all feeds to md document

        for f in infiles:

            infullpath = os.path.join(inpath, f)

            if os.path.isfile(infullpath):
                outfullpath = os.path.join(outpath, os.path.splitext(f)[0] + '.md')

                try:
                    d = feedparser.parse(infullpath)

                    #print(d['entries'][0]['content'][0]['value'])
                    feed_to_md_file(d, outfullpath)
                except:
                    print("Bad file {}".format(infullpath))
