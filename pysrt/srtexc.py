"""
Exception classes
"""


class SubRipError(Exception):
    """
    Pysrt's base exception
    """
    pass


class InvalidTimeString(SubRipError):
    """
    Raised when parser fail on bad formated time strings
    """
    pass


class InvalidItem(SubRipError):
    """
    Raised when parser fail to parse a sub title item
    """
    pass
