class Py3oArray(dict):
    def __init__(self, iterator):
        """
        This class should contain information about the for loops variable.
        :param name: The name of the attribute holding the array
        """
        super(Py3oArray, self).__init__()
        self.arrays = {}
        self.names = iterator.get_names()

    def add_array(self, array):
        """
        This function allows you to add a child Py3oArray.
        :param array: The Py3oArray to store.
        """
        self.arrays[array.name] = array

    def get_context(self):
        """
        :return: A dictionary containing all defined attrs and childs
         in this array
        """
        return {
            key: None
            for key in self.arrays
        }


class Py3oAttribute(tuple):
    def get_names(self):
        return self


class Py3obuiltin(object):
    def get_names(self):
        raise NotImplementedError