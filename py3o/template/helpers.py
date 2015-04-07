import ast
import pprint
from textwrap import dedent
from py3o.template.data_struct import Py3oModule, Py3oName, Py3oArray, \
    Py3oObject


# This is used as global context key in the convertor
PY3O_MODULE_KEY = '__py3o_module__'


class Py3oConvertor(ast.NodeVisitor):
    def __call__(self, source):
        """
        When called, this class will unfold the ast, and for each node,
          try to represent its content in a JSON format.
        A local_context is created at the beginning, initialized
          with the user_data, and is supposed to hold the defined variables
          and their values (taken from the user_data dict) in the form:
            {'var': value}
        You can also insert function in the local_context so they will be kwown
        """

        # Parse the source code, and call the recursive 'visit' function
        source = dedent(source)
        self._source = source
        self._ast = ast.parse(source)

        return self.visit(self._ast, {})

    def visit(self, node, local_context=None):
        """Call the node-class specific visit function."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, local_context)

    def visit_Module(self, node, local_context):
        module = Py3oModule()
        local_context[PY3O_MODULE_KEY] = module

        for n in node.body:
            self.visit(n, local_context)

        return module

    def set_last_item(self, py3o_obj, inst):
        # Return the last dictionary item of the chain
        tmp = py3o_obj
        keys = tmp.keys()
        while keys:
            next_tmp = tmp[next(iter(keys))]
            next_keys = next_tmp.keys()
            if not next_keys:
                break
            tmp, keys = next_tmp, next_keys
        tmp[next(iter(keys))] = inst
        return tmp

    def update(self, d, n):
        """
        Update recursively the dict d with the dict n
        """
        for key, value in n.items():
            if isinstance(value, Py3oObject):
                if key in d:
                    r = self.update(d[key], value)
                else:
                    r = value
                d[key] = r
        return d

    def bind_target(self, iterable, target, context):
        """ This function fill the context according to the iterable and
         target and return a new_context to pass through the for body
        :return: dict
        """
        new_context = context.copy()

        if isinstance(iterable, str):
            if iterable in context:
                new_context[target] = new_context[iterable]
            else:
                new_context[target] = Py3oArray()
                new_context[PY3O_MODULE_KEY].update(
                    {iterable: new_context[target]}
                )

        if isinstance(iterable, list):
            # Convert the list into a context
            iter_context = self.list_to_py3o_name(iterable, context)
            # Now replace the last item by a Py3oArray()
            new_array = Py3oArray()
            self.set_last_item(iter_context, new_array)
            key = next(iter(iter_context))
            if key in context:
                # Update the related context with the new attribute access
                self.update(new_context[key], iter_context[key])
                new_context[target] = new_array
            else:
                self.update(
                    new_context[PY3O_MODULE_KEY],
                    {key: iter_context[key]}
                )
                new_context[target] = new_array

        return new_context

    def visit_For(self, node, local_context):
        """Update the context so our chidren have access
         to the newly declared variable.
        """

        # Bind iterable and target
        body_context = self.bind_target(
            self.visit(node.iter, local_context),
            self.visit(node.target, local_context),
            local_context,
        )

        for n in node.body:
            self.visit(n, body_context)

    def visit_Name(self, node, local_context):
        return node.id

    def visit_Attribute(self, node, local_context):
        """ Visit our children and return a tuple
         representing the path of attribute
        :return: tuple
        """
        value = self.visit(node.value, local_context)
        if isinstance(value, str):
            # Create a tuple with the two values
            return [value, node.attr]
        if isinstance(value, list):
            # Add the string to the tuple
            value.append(node.attr)
            return value

    # TODO: Manage Tuple in for loop (for i, j in enumerate(list))
    # def visit_Tuple(self, node, local_context):
    #     raise NotImplementedError(
    #         "The tuple interpretation is not already done."
    #     )
    #     ctx = node.ctx
    #     if isinstance(ctx, ast.Store):
    #         res = []
    #         # Browse each elements of Tuple and visit them
    #         for n in node.elts:
    #             res.append(self.visit(n, local_context))
    #         return res
    #     else:
    #         raise NotImplementedError(
    #             "The ctx '%s' is not interpreted for Tuple" % type(ctx)
    #         )

    def list_to_py3o_name(self, value, local_context):
        """ Return a context corresponding to the list
        """
        res = Py3oName()
        tmp = res
        for elem in value:
            tmp[elem] = Py3oName()
            tmp = tmp[elem]
        return res

    def visit_Expr(self, node, local_context):
        value = self.visit(node.value, local_context)
        if isinstance(value, list):
            # An attr access, convert the list into Py3oName dicts
            #  and add it to the local_context
            expr = self.list_to_py3o_name(value, local_context)
            key = next(iter(expr.keys()))
            if key in local_context:
                self.update(local_context[key], expr[key])
            else:
                local_context[PY3O_MODULE_KEY].update(expr)
        elif isinstance(value, str):
            # Tell the object that this is a direct access
            if value in local_context:
                local_context[value].direct_access = True


def ast2tree(node, include_attrs=True):  # pragma: no cover
    def _transform(node):
        if isinstance(node, ast.AST):
            fields = ((a, _transform(b))
                      for a, b in ast.iter_fields(node))
            if include_attrs:
                attrs = ((a, _transform(getattr(node, a)))
                         for a in node._attributes
                         if hasattr(node, a))
                return node.__class__.__name__, dict(fields), dict(attrs)
            return node.__class__.__name__, dict(fields)
        elif isinstance(node, list):
            return [_transform(x) for x in node]
        elif isinstance(node, str):
            return repr(node)
        return node
    if not isinstance(node, ast.AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    return _transform(node)


def pformat_ast(node, include_attrs=False, **kws):  # pragma: no cover
    return pprint.pformat(ast2tree(node, include_attrs), **kws)
