Introduction
============

This work was originally inspired by `relatorio`_ and diverged in
implementation, scope and ambitions. Relatorio has many more features
when py3o.template is mainly focused on ODT, ODS and text output.

py3o is an elegant and scalable solution to design
reports using LibreOffice.
py3o.template is the templating component that takes care of
merging your data sets with a corresponding templated OpenOffice document.

It is plateform independent and does not require LibreOffice/OpenOffice itself
to generate an ODF file.

If you want to generate a PDF or any other supported output format you will then
need to have a server with either LibreOffice or OpenOffice and to install
the `py3o.renderserver`_ on it. We also provide a docker image on
the `docker hub`_

If you want to have templating fusion & document conversion in one
single web service usable from any language with just HTTP/POST you can install
`py3o.fusion`_ server. Which also exists as a `docker image`_

Python 3 support
================

py3o.template is python3 ready. But, yes there is a but... alas!,
you'll need to install a trunk version of Genshi::

    $ # activate your python env...
    $ svn checkout http://svn.edgewall.org/repos/genshi/trunk genshi_trunk
    $ cd genshi_trunk
    $ python setup.py build
    $ python setup.py install

We tested this with revision 1271.
When genshi 0.8 is released we can officially say we support Python3 out of
the box.

Full Documentation
==================

We `provide a documentation`_ for this package. If anything is not correctly
explained, please! create a ticket `in our ticketing system`_

Example Usage
=============

Below is an example that you can find in the source code inside the examples
directory.

::

    from py3o.template import Template

    t = Template("py3o_example_template.odt", "py3o_example_output.odt")

    t.set_image_path('staticimage.logo', 'images/new_logo.png')


    class Item(object):
        pass

    items = list()

    item1 = Item()
    item1.val1 = 'Item1 Value1'
    item1.val2 = 'Item1 Value2'
    item1.val3 = 'Item1 Value3'
    item1.Currency = 'EUR'
    item1.Amount = '12345.35'
    item1.InvoiceRef = '#1234'
    items.append(item1)

    for i in xrange(1000):
        item = Item()
        item.val1 = 'Item%s Value1' % i
        item.val2 = 'Item%s Value2' % i
        item.val3 = 'Item%s Value3' % i
        item.Currency = 'EUR'
        item.Amount = '6666.77'
        item.InvoiceRef = 'Reference #%04d' % i
        items.append(item)

    document = Item()
    document.total = '9999999999999.999'

    data = dict(items=items, document=document)
    t.render(data)

Changelog
=========

0.9.7 Dec. 8 2015
~~~~~~~~~~~~~~~~~

  - This release focuses on the parser. If you
    don't use the template parser you can skip this release as it does not
    change anything else.
  - Fix a bug where the body of the if blocks were not evaluated
    by the parser
  - Refactoring tests for clearer reading
  - fix some missing/untested functions
  - remove NotImplementedError from coverage

0.9.6 Nov. 20 2015
~~~~~~~~~~~~~~~~~~

  - Fixed formatting function 
  - Fixed if="" functionality that was not correctly parsed
  - Display empty string instead of "False" when browsing relational field
  - Code formatting in the ast parser

0.9.5 Oct. 30 2015
~~~~~~~~~~~~~~~~~~

  - 0.9.5 is just a rerelease of 0.9.4 with this README correctly
    amended...

  - Added support for formatting functions in the template in
    order to control date number localization
  - Added reference to original inspiration in the README
  - Added example source code for ODS output.
  - Fixed a memory usage in case of big output file size that
    was introduced by the dynamic image feature.
  - Introduced an experimental TextTemplate
  - Fixed support for special cases where page breaks removals
    removed trailing text (thanks to agix)

0.9.3 Jun. 26 2015
~~~~~~~~~~~~~~~~~~

  - Introduced dynamic image support (ie: pass in image data in the input
    iterator) and use it to insert images on the fly in the report)

0.9.2 Jun. 26 2015
~~~~~~~~~~~~~~~~~~

  - WARNING: if you used the old image replacement system, you
   need to update your code to set static image from this::

      # old way
      t.set_image_path('logo', 'images/new_logo.png')

      # You should now set it like this instead

      # new way. Note the 'staticimage.' prefix added just before 'logo'
      t.set_image_path('staticimage.logo', 'images/new_logo.png')

  - WARNING: after updating your code you must also update your template
    to prefix your static images names with the 'staticimage.' prefix.

  - Added dynamic images support. You can now add images instructions inside
    for loops or anywhere in your templates and pass the image data
    inside your objects attributes.
  - Added support for image data (dynamic ones) being passed-in as base64
    data. This is useful for some clients like `Odoo's report_py3o`_ because
    they store image data as base64 encoded fields.

.. _Odoo's report_py3o: https://bitbucket.org/xcg/report_py3o

0.9.1 Jun. 3 2015
~~~~~~~~~~~~~~~~~

  - Fixed parser to read from the var name instead of its description,
    if you dont use the helper tool to introspect your reports this release
    is of no importance to you as it only fixes this particular point.

0.9 Jan. 8 2015
~~~~~~~~~~~~~~~~

  - Added support for soft page breaks


0.8 Nov. 19 2014
~~~~~~~~~~~~~~~~

  - Added better unit tests
  - Fixed corner cases in the variable introspection mechanism
  - Better handling of "ignore_undefined" that now also allows undefined images

0.7 Oct. 15 2014
~~~~~~~~~~~~~~~~

  - Added Python3 support
  - Fixed a problem with validity of output in case the template contains
    a text:list inside a for loop
  - Added new public methods to help report servers introspect the template
    data dictionary
  - Added real unit tests (96% coverage ATM, way to go test team!)

Contributors
============

By order of contribution date:

  - `Florent Aide`_
  - `Emmanuel Cazenave`_
  - `jon1012`_
  - `Eugene Morozov`_
  - `Houzéfa Abbasbay`_
  - `Torsten Irländer`_
  - `Sergey Fedoseev`_
  - `Vincent Lhote-Hatakeyama`_
  - `Anael Lorimier`_
  - `Björn Ricks`_
  - `Agix`_

.. _Florent Aide: https://bitbucket.org/faide
.. _Emmanuel Cazenave: https://bitbucket.org/cazino
.. _jon1012: https://bitbucket.org/jon1012
.. _Eugene Morozov: https://bitbucket.org/mojo
.. _Houzéfa Abbasbay: https://bitbucket.org/houzefa-abba
.. _Torsten Irländer: https://bitbucket.org/ti
.. _Sergey Fedoseev: https://bitbucket.org/sir_sigurd
.. _Vincent Lhote-Hatakeyama: https://bitbucket.org/vincent_lhote
.. _Anael Lorimier: https://bitbucket.org/alorimier
.. _Björn Ricks: https://bitbucket.org/bjoernricks
.. _Agix: https://bitbucket.org/agix

.. _py3o.renderserver: https://bitbucket.org/faide/py3o.renderserver/
.. _provide a documentation: http://py3otemplate.readthedocs.org
.. _in our ticketing system: https://bitbucket.org/faide/py3o.template/issues?status=new&status=open
.. _docker hub: https://registry.hub.docker.com/u/xcgd/py3oserver-docker/
.. _py3o.fusion: https://bitbucket.org/faide/py3o.fusion
.. _docker image: https://registry.hub.docker.com/u/xcgd/py3o.fusion
.. _relatorio: http://relatorio.tryton.org/
