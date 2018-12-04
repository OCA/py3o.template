from py3o.template import TextTemplate

t = TextTemplate("simple_text.txt", "text.txt")


class Item(object):
    pass


items = list()

# if you are using python 2.x you should use xrange
for i in range(124):
    item = Item()
    item.col1 = "Item%s Value1" % i
    item.col2 = i
    item.col3 = "type%s" % (i % 2)
    item.col4 = "Some description that never changes"

    items.append(item)

data = dict(items=items)
t.render(data)
