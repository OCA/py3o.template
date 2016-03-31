"""This file contains all the data structures used by Py3oConvertor
See the docstring of Py3oConvertor.__call__() for further information
"""
from numbers import Number


class Py3oDataError(Exception):
    pass


class Py3oObject(dict):
    """ Base class to be inherited.
    """
    def render(self, data):  # pragma: no cover
        raise NotImplementedError("This function should be overriden")

    def __repr__(self):  # pragma: no cover
        res = super(Py3oObject, self).__repr__()
        return "{}({})".format(
            self.__class__.__name__,
            res
        )

    def get_size(self):
        """Return the max depth of the object
        """
        sizes = [val.get_size() for val in self.values()]
        if not sizes:
            return 0
        return max(sizes) + 1

    def get_key(self):
        """Return the first key
        """
        return next(iter(self.keys()))

    def get_tuple(self):
        """Return the value of the Py3oObject as a tuple.
        As a default behavior, the object returns itself as a single.
        """
        return self,

    def unpack(self, target):
        self_tup = self.get_tuple()
        target_tup = target.get_tuple()
        diff = len(target_tup) - len(self_tup)
        if diff != 0:  # pragma: no cover
            raise ValueError(u"Unpack Error")
        return zip(target_tup, self_tup)

    def rupdate(self, other):
        """Update recursively the Py3oObject self with the Py3oObject other.
        Example:
        self = Py3oObject({
            'a': Py3oObject({}),
            'b': Py3oObject({
                'c': Py3oObject({}),
            }),
        })
        other = Py3oObject({
            'b': Py3oObject({
                'd': Py3oObject({}),
            }),
        })
        res = Py3oObject({
            'a': Py3oObject({}),
            'b': Py3oObject({
                'c': Py3oObject({}),
                'd': Py3oObject({}),
            }),
        })
        """
        for key, value in other.items():
            if key in self:
                self[key].rupdate(value)
            else:
                self[key] = value

    def rget(self, other):
        """Get the value for the path described by the other Py3oObject.

        Recursively checks that the values in other can be found in self.

        The method returns the values of self and other at the point where
        the search stopped.
        If other is a leaf, the search stops sucessfully. The method returns
        True, the value that corresponds to the path described by other, and
        the leaf in question.
        If other cannot be found in self, the search stops unsuccessfully.
        The method returns False, the value that corresponds to the deepest
        point reached in self, and the rest of the path.

        Example:
        self = Py3oObject({
            'a': Py3oObject({}),
            'b': Py3oObject({
                'c': Py3oObject({}),
            }),
        })
        other = Py3oObject({
            'b': Py3oObject({
                'd': Py3oObject({}),
            }),
        })
        res = (
            False,
            Py3oObject({'c': Py3oObject({})}),  # is self['b']
            Py3oObject({'d': Py3oObject({})}),  # is other['b']
        )
        if other['b'] was a leaf, res[0] would be True and res[2] the leaf.

        :return: A triplet:
          - True if the search was successful, False otherwise
          - The active sub-element of self when the search stopped
          - The active sub-element of other when the search stopped
        """
        if not other:
            return True, self, other
        other_key = other.get_key()
        if other_key in self:
            return self[other_key].rget(other[other_key])
        else:
            return False, self, other


class Py3oModule(Py3oObject):
    def render(self, data):
        """ This function will render the datastruct according
         to the user's data
        """
        res = {}
        for key, value in self.items():
            subdata = data.get(key, None)
            if subdata is None:
                raise Py3oDataError(
                    "The key '%s' must be present"
                    " in your data dictionary" % key
                )
            # Spread only the appropriate data to its children
            val = value.render(data.get(key))
            if val is not None:
                res[key] = val
        return res


class Py3oArray(Py3oObject):
    """ A class representing an iterable value in the data structure.
    The attribute direct_access will tell if this class should be considered
     as a list of dict or a list of values.
    """
    def __init__(self):
        super(Py3oArray, self).__init__()
        self.direct_access = False

    def render(self, data):
        """ This function will render the datastruct according
        to the user's data
        """
        if self.direct_access:
            return data
        if not self:  # pragma: no cover
            return None
        res = []
        for d in data:
            tmp_dict = {}
            for key, value in self.items():
                # Spread only the appropriate data to its children
                tmp_dict[key] = value.render(getattr(d, key))
            res.append(tmp_dict)
        return res


class Py3oName(Py3oObject):
    """ This class holds information of variables.
    Keys are attributes and values the type of this attribute
     (another Py3o class or a simple value)
    i.e.: i.egg -> Py3oName({'i': Py3oName({'egg': Py3oName({})})})
    """
    def render(self, data):
        """ This function will render the datastruct according
        to the user's data
        """
        if not self:
            # We only send False values if the value is a number
            # otherwise we convert the False into an empty string
            if isinstance(data, Number):
                return data
            return data or u""
        res = {}

        for key, value in self.items():
            # Spread only the appropriate data to its children
            res[key] = value.render(getattr(data, key))
        return res


class Py3oCall(Py3oObject):
    """This class holds information of function call.
    'name' holds the name of function as a Py3oName
    The keys are the arguments as:
        - numeric keys are positional arguments oredered ascendently
        - string keys are keywords arguments
    """

    return_format = None

    def __init__(self, name, dict):
        super(Py3oCall, self).__init__(dict)
        self.name = name

    def get_tuple(self):  # pragma: no cover
        raise SyntaxError(u"Can't assign to function call")

    def unpack(self, target):
        target_tup = target.get_tuple()
        args = set(self.keys())

        if self.return_format is None:
            # Generic/unknown function, do not make assumptions about targets
            res = [(target, None) for target in target_tup]
            res += [(None, self[arg]) for arg in args]

        else:
            # Bind targets to function arguments according to return_format
            return_value = []
            for return_var in self.return_format:
                if return_var is None:
                    return_value.append(Py3oDummy())
                else:
                    return_value.append(self.get(return_var, None))

            if len(return_value) == len(target_tup):
                res = zip(target_tup, return_value)

            # TODO: Manage Py3oContainer values inside for loop body
            # elif len(target_tup) == 1:
            #     res = [(target_tup[0], Py3oContainer(return_value))]
            #     res += [(self[arg], None) for arg in args]

            else:  # pragma: no cover
                raise ValueError(u"Unpack Error")

        return res


class Py3oEnumerate(Py3oCall):
    """Represent an enumerate call"""
    return_format = (None, 0)


class Py3oContainer(Py3oObject):
    """Represent a container defined in the template.
    This container can be:
    _ A literal list, tuple, set or dict definition
    _ A tuple of variables that are the target of an unpack assignment
    """
    def __init__(self, values):
        super(Py3oContainer, self).__init__()
        self.values = values

    def get_tuple(self):
        """Return the container's values in a tuple"""
        return tuple(self.values)


class Py3oDummy(Py3oObject):
    """ This class holds temporary dict, or unused attribute
     such as counters from enumerate()
    """
    pass


class Py3oBuiltin(Py3oObject):
    """ This class holds information about builtins
    """

    builtins = {
        'enumerate': Py3oEnumerate
    }

    @classmethod
    def from_name(cls, name=None):
        """Return the Py3oObject subclass for the given built-in name
        Return None if the name does not correspond to a builtin.

        :param name: A Py3oObject instance that represent a name/attribute path
        :return: A Py3oObject subclass or None
        """
        name_key = name.get_key()
        builtin = cls.builtins.get(name_key)
        # TODO: uncomment to implement standard modules in cls.builtins
        # if builtin and name.get_size() > 1:
        #     if isinstance(builtin, Py3oBuiltin):
        #         builtin = builtin.from_name(name[name_key])
        #     else:
        #     builtin = None
        return builtin
