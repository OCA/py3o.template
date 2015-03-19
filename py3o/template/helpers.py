import ast
import pprint
from textwrap import dedent
from py3o.template.data_struct import Py3oArray


class Py3oConvertor(ast.NodeVisitor):
    def __call__(self, source, user_data):
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

        return self.visit(self._ast, user_data)

    @staticmethod
    def _format_for_target(target):
        """Return an uniform structure of variable
        """
        #TODO: This may not contains anything else tuple or str, but if it
        #TODO:   does, we should find a way to raise an error
        return tuple(target)

    def _get_body_context(self, targets, iterator, local_context):
        vals = iterator()
        new_context = local_context.copy()
        for target, val in zip(targets, vals):
            new_context[target] = val
        return new_context

    def visit(self, node, local_context=None):
        """Call the node-class specific visit function."""
        if local_context is None:
            local_context = {}
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, local_context)

    def visit_Module(self, node, local_context):
        data_struct = {}
        for n in node.body:
            data_struct.update(
                self.visit(n, local_context)
            )
        return data_struct

    def visit_For(self, node, local_context):
        """Visit a for node"""

        # Get the iterator that should be either one of those type:
        #   - Py3oAttribute,
        #   - Py3oBuiltin,
        iterator = self.visit(node.iter, local_context)

        # create a Py3oArray obj to hold our loop information
        array = Py3oArray(iterator)
        # iter should be an iterable taken from local_context

        # target will be a tuple of all newly declared variables
        targets = self._format_for_target(
            self.visit(node.target, local_context)
        )
        print(targets)

        # Iterate through each element found in the local_context
        # for this iterable and create a new context
        body_context = self._get_body_context(
            targets, iterable, local_context
        )
        print(body_context)
        for n in node.body:
            local_context.update(self.visit(n, body_context))
        return local_context

    def visit_Name(self, node, local_context):
        """A simple name that should either be stored or loaded"""
        var = node.id

        # Return the string name
        return var

    def visit_Attribute(self, node, local_context):
        """Visit an attribute and return the corresponding
         tuple (attr1, attr2, ...)
        """
        ctx = node.ctx
        if isinstance(ctx, ast.Load):
            value = self.visit(node.value, local_context)
            if isinstance(value, dict):
                return list(value.keys())[0], node.attr
            elif isinstance(value, tuple):
                return value + (node.attr,)
        else:
            raise NotImplementedError(
                "The ctx '%s' is not interpreted for Tuple" % type(ctx)
            )

    def visit_Tuple(self, node, local_context):
        """Visit a Tuple"""
        ctx = node.ctx
        if isinstance(ctx, ast.Store):
            res = []
            # Browse each elements of Tuple and visit them
            for n in node.elts:
                res.append(self.visit(n, local_context))
            return res
        else:
            raise NotImplementedError(
                "The ctx '%s' is not interpreted for Tuple" % type(ctx)
            )

    def visit_Expr(self, node, local_context):
        """Visit an expression and get its value"""


def ast2tree(node, include_attrs=True):
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


def pformat_ast(node, include_attrs=False, **kws):
    return pprint.pformat(ast2tree(node, include_attrs), **kws)
