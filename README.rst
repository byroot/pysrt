pysrt is a Python library used to edit or create SubRip files.

Basic Usage
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
    >>> first_sub.shift(seconds=1) # Move the first sub 1 second later
    >>> first_sub.start += {'seconds': -1} # Make the first sub start 1 second earlier
    
Removing: ::
    
    >>> del subs[12]
    
Slicing: ::
    
    >>> part = subs.slice(starts_after={'minutes': 2, seconds': 30}, ends_before={'minutes': 3, 'seconds': 40})
    >>> part.shift(seconds=-2)
    
Saving changes: ::
    
    >>> subs.save('other/path.srt', encoding='utf-8')
