# ArgsUtils.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

#___________________________________________________________________________________________________ ArgsUtils
class ArgsUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                      C L A S S

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getFrom
    @classmethod
    def getFrom(cls, name, key, defaultValue =None, kwargs =None, args =None, index =None):
        src = cls.get(name, None, kwargs, args, index)
        if not src:
            return defaultValue
        if isinstance(src, dict):
            return src.get(key, defaultValue)

        return getattr(src, key, defaultValue)

#___________________________________________________________________________________________________ get
    @classmethod
    def get(cls, name, defaultValue =None, kwargs =None, args =None, index =None):
        if args and not index is None and (index < 0 or index < len(args)):
            return args[index]

        try:
            if isinstance(name, basestring):
                if name in kwargs:
                    return kwargs[name]
            else:
                for n in name:
                    if n in kwargs:
                        return kwargs[n]
        except Exception, err:
            pass

        return defaultValue

#___________________________________________________________________________________________________ getAsList
    @classmethod
    def getAsList(cls, name, kwargs =None, args =None, index =None, defaultValue =None):
        res = ArgsUtils.get(name, None, kwargs, args, index)
        if res is None:
            return defaultValue if defaultValue else []

        if not isinstance(res, list):
            return [res]

        return res

#___________________________________________________________________________________________________ extract
    @classmethod
    def extract(cls, name, defaultValue, kwargs, args =None, index =None):
        """ Returns the value if one was specified and if the argument was in the kwargs dictionary
            deletes it.
        """
        value = ArgsUtils.get(name, defaultValue, kwargs, args, index)
        if name in kwargs:
            del(kwargs[name])
        return value

