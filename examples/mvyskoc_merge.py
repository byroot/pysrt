#!/usr/bin/env python
# -*- coding: utf8 -*-

# Copyright mvyskoc (https://github.com/mvyskoc)

# This script mix 2 subtitles files in different languages in one file
# to allow multiple people with different language to watch a movie together
# or to help someone to learn a foreign language

# See https://github.com/byroot/pysrt/issues/17 for more detailed information

import sys
import getopt
from pysrt import SubRipFile
from pysrt import SubRipItem
from pysrt import SubRipTime


def join_lines(txtsub1, txtsub2):
    if (len(txtsub1) > 0) & (len(txtsub2) > 0):
        return txtsub1 + '\n' + txtsub2
    else:
        return txtsub1 + txtsub2


def find_subtitle(subtitle, from_t, to_t, lo=0):
    i = lo
    while (i < len(subtitle)):
        if (subtitle[i].start >= to_t):
            break

        if (subtitle[i].start <= from_t) & (to_t  <= subtitle[i].end):
            return subtitle[i].text, i
        i += 1

    return "", i



def merge_subtitle(sub_a, sub_b, delta):
    out = SubRipFile()
    intervals = [item.start.ordinal for item in sub_a]
    intervals.extend([item.end.ordinal for item in sub_a])
    intervals.extend([item.start.ordinal for item in sub_b])
    intervals.extend([item.end.ordinal for item in sub_b])
    intervals.sort()

    j = k = 0
    for i in xrange(1, len(intervals)):
        start = SubRipTime.from_ordinal(intervals[i-1])
        end = SubRipTime.from_ordinal(intervals[i])

        if (end-start) > delta:
            text_a, j = find_subtitle(sub_a, start, end, j)
            text_b, k = find_subtitle(sub_b, start, end, k)

            text = join_lines(text_a, text_b)
            if len(text) > 0:
                item = SubRipItem(0, start, end, text)
                out.append(item)

    out.clean_indexes()
    return out

def usage():
    print "Usage: ./srtmerge [options] lang1.srt lang2.srt out.srt"
    print
    print "Options:"
    print "  -d <milliseconds>         The shortest time length of the one subtitle"
    print "  --delta=<milliseconds>    default: 500"
    print "  -e <encoding>             Encoding of input and output files."
    print "  --encoding=<encoding>     default: utf_8"


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hd:e:', ["help", "encoding=", "delta="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    #Settings default values
    delta = SubRipTime(milliseconds=500)
    encoding="utf_8"
    #-

    if len(args) <> 3:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-d", "--delta"):
            delta = SubRipTime(milliseconds=int(a))
        elif o in ("-e", "--encoding"):
            encoding = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()

    subs_a = SubRipFile.open(args[0], encoding=encoding)
    subs_b = SubRipFile.open(args[1], encoding=encoding)
    out = merge_subtitle(subs_a, subs_b, delta)
    out.save(args[2], encoding=encoding)

if __name__ == "__main__":
    main()