pysrt
=============

pysrt is a Python library used to edit or create SubRip files.

Foreword
====================

pysrt is mainly designed as a library, but if you are experiencing troubles
with bad subtitles you can first try to use `ruby-osdb <https://github.com/byroot/ruby-osdb>`_
which will try to find the best subtitle for your movie. If you are still unlucky
pysrt also provide an ``srt`` command useful for either shift, split, or rescale a
*.srt* file.

Command Usage
=====================

Shifting: ::
  
    $ srt -i shift 2s500ms movie.srt

Spliting: ::

    $ srt split 58m26s movie.srt

Rescaling: ::

    $ srt -i rate 23.9 25 movie.srt

Installation
=================

pysrt is available on pypi. To intall it you can use either

pip: ::
    
    $ sudo pip install pysrt3
    
or distutils: ::

    $ sudo easy_install pysrt3

**Note**: The package name that runs on python 3 is ``pysrt3``. The ``pysrt``
package is compatible with python 2.x.

Library Usage
=============

Import: ::

    >>> from pysrt import SubRipFile
    
Parsing: ::

    >>> subs = SubRipFile.open('some/file.srt')
    # If you get a UnicodeDecodeError try to specify the encoding
    >>> subs = SubRipFile.open('some/file.srt', encoding='iso-8859-1')
    
SubRipFile are list-like objects of SubRipItem instances: ::
    
    >>> len(first_sub)
    >>> first_sub = subs[0]
    
SubRipItem instances are editable just like pure Python objects: ::
    
    >>> first_sub.text = "Hello World !"
    >>> first_sub.start.seconds = 20
    >>> first_sub.end.minutes = 5
    
Shifting: ::

    >>> subs.shift(seconds=-2) # Move all subs 2 seconds earlier
    >>> subs.shift(minutes=1)  # Move all subs 1 minutes later
    >>> subs.shift(ratio=25/23.9) # convert a 23.9 fps subtitle in 25 fps
    >>> first_sub.shift(seconds=1) # Move the first sub 1 second later
    >>> first_sub.start += {'seconds': -1} # Make the first sub start 1 second earlier
    
Removing: ::
    
    >>> del subs[12]
    
Slicing: ::
    
    >>> part = subs.slice(starts_after={'minutes': 2, seconds': 30}, ends_before={'minutes': 3, 'seconds': 40})
    >>> part.shift(seconds=-2)
    
Saving changes: ::
    
    >>> subs.save('other/path.srt', encoding='utf-8')
