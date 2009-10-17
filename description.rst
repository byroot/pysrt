pysrt is a Python library used to edit or create SubRip files.

Usage
=====

::

    from pysrt import SubRipFile, SubRipItem, SubRipTime
    subs = SubRipFile('some/file.srt')
    subs[42].end.hours += 3
    subs[42].sub_title = "Never end !"

    #equivalent
    part = SubRipFile(i for i in subs if i.end > SubRipTime(0, 0, 40))
    part = SubRipFile(i for i in subs if i.end > (0, 0, 40))
    part = SubRipFile(i for i in subs if i.end > {'seconds': 40})

    part.shift(seconds=-2)
    subs.save('other/path.srt', 'utf-8')
