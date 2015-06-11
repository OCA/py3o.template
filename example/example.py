from py3o.template import Template

t = Template("py3o_example_template.odt", "py3o_example_output.odt")

t.set_image_path('staticimage.logo', 'images/new_logo.png')


class Item(object):
    pass

items = list()

item1 = Item()
item1.val1 = 'Item1 Value1'
item1.image = open('images/dot1.png', 'rb').read()
item1.val3 = 'Item1 Value3'
item1.Currency = 'EUR'
item1.Amount = '12345.35'
item1.InvoiceRef = '#1234'
items.append(item1)

# if you are using python 2.x you should use xrange
for i in range(124):
    item = Item()
    item.val1 = 'Item%s Value1' % i
    item.image = open('images/dot%s.png' % (i % 2), 'rb').read()
    item.val3 = 'Item%s Value3' % i
    item.Currency = 'EUR'
    item.Amount = '6666.77'
    item.InvoiceRef = 'Reference #%04d' % i
    items.append(item)

document = Item()
document.total = '9999999999999.999'

data = dict(items=items, document=document)
t.render(data)
