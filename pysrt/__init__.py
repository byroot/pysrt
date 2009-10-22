# -*- coding: utf-8 -*-
'''
>>> s = SubRipFile.from_string("""1
... 00:00:02,207 --> 00:00:03,221
... ÉCHEC !
...
... 2
... 00:00:30,371 --> 00:00:33,981
... Le Retour de l'Enfant Prodigue
...
... 3
... 00:00:35,619 --> 00:00:37,277
... Ce qui veut dire...
...
... 4
... 00:00:37,433 --> 00:00:39,761
... un bénéfice, cette année, de...
...
... 5
... 00:00:39,933 --> 00:00:43,121
... - 1 800 milliards de milliards.
... - Splendide !
...
... 7
... 00:00:43,410 --> 00:00:45,136
... Sans compter les revenus subsidiaires
... """)
>>> len(s)
6
>>> s.clean_ids()
>>> s[5].id
6
>>> s[-1].end.seconds
45
>>> part = SubRipFile(i for i in s if i.end > (0, 0, 40))
>>> len(part)
2
>>> len(s.slice(ends_after=(0, 0, 40)))
2
>>> part = SubRipFile(i for i in s if i.end > {'seconds': 40})
>>> len(part)
2
>>> len(s.slice(ends_after={'seconds': 40}))
2
>>> part.shift(seconds=-5)
>>> part[1].start.minutes += 5
>>> item = s[-1]
>>> item.end.seconds
40
>>> tuple(item.start), tuple(SubRipTime(*tuple(item.start)))
((0, 5, 38, 410), (0, 5, 38, 410))
>>> tuple(item.start) == SubRipTime(*tuple(item.start))
True
>>> item.start <= (0, 5, 39)
True
>>> item.start >= (0, 5, 37)
True
>>> item.start == (0, 5, 38, 410)
True

>>> t= SubRipTime(milliseconds=1)
>>> t.seconds, t.ordinal
(0, 1)
>>> t.seconds += 1
>>> t.seconds, t.ordinal
(1, 1001)
>>> tuple(t + {'seconds': 1})
(0, 0, 2, 1)
>>> tuple(t - {'seconds': 1})
(0, 0, 0, 1)

'''
from srttime import SubRipTime
from srtitem import SubRipItem
from srtfile import SubRipFile
from srtexc import InvalidItem, InvalidTimeString

if __name__ == "__main__":
    import doctest
    doctest.testmod()
