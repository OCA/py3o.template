from py3o.template import Template

t = Template("simple_calc.ods", "calc.ods")


class Item(object):
    pass

items = list()

# if you are using python 2.x you should use xrange
for i in range(124):
    item = Item()
    item.col1 = 'Item%s Value1' % i
    item.col2 = i
    item.col3 = 'type%s' % (i % 2)
    item.col4 = 'Some description that never changes'

    item.image = open('images/dot%s.png' % (i % 2), 'rb').read()

    items.append(item)

data = dict(items=items)
t.render(data)
