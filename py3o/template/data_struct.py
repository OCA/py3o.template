class Py3oModule(dict):
    def jsonify(self, data):
        """ This function will render the datastruct according
         to the user's data
        :param data: User data to use for jsonification
        :return: dict
        """
        for key, value in self.items():
            value.jsonify(getattr(data, key))

    def __repr__(self):
        res = super(Py3oModule, self).__repr__()
        return "Py3oModule(" + res + ")"


class Py3oForList(dict):
    """ This class holds python for list information
    """
    def __init__(self, iterable, target):
        """
        This class holds array information
        :param iterable: Py3oName, Py3oAttribute, Py3oBuiltin
        :param target: tuple
        """
        self.iterable = iterable
        self.target = target
        super(Py3oForList, self).__init__()

    def bind_target(self):
        """
        This tries to create a dict that bind target and iterable
        """
        if isinstance(self.iterable, Py3oAttribute):
            self[self.target[0]] = Py3oArray()
        else:
            raise NotImplementedError

    def __repr__(self):
        res = super(Py3oForList, self).__repr__()
        return "Py3oForList(" + res + ")"


class Py3oArray(dict):
    """ This class should be filled up with used attr from it
    """
    def __repr__(self):
        res = super(Py3oArray, self).__repr__()
        return "Py3oArray(" + res + ")"


class Py3oBuiltin(object):
    pass


class Py3oName(dict):
    def __repr__(self):
        res = super(Py3oName, self).__repr__()
        return "Py3oName(" + res + ")"


class Py3oDummy(dict):
    """ This class holds unused defined attribute,
     such as counters from enumerate()
    """
    pass