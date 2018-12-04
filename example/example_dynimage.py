from py3o.template import Template

t = Template("asimage.odt", "asimage_output.odt")

# t.set_image_path('logo', 'images/new_logo.png')


class Item(object):
    pass


item = Item()
item.image = open("images/new_logo.png", "rb").read()
item.image2 = open("images/new_logo.png", "rb").read()
item.image3 = open("images/new_logo.png", "rb").read()

data = {"object": item}
t.render(data)
