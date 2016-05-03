# -*- encoding: utf-8 -*-
import datetime
import os
import unittest
import zipfile
import traceback
import copy
import base64

import lxml.etree
import pkg_resources
import six

from io import BytesIO

from genshi.template import TemplateError
from pyjon.utils import get_secure_filename

from py3o.template import Template, TextTemplate, TemplateException
from py3o.template.main import XML_NS, get_soft_breaks

if six.PY3:
    # noinspection PyUnresolvedReferences
    from unittest.mock import Mock
elif six.PY2:
    # noinspection PyUnresolvedReferences
    from mock import Mock


class TestTemplate(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        pass

    def test_example_1(self):
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_example_template.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)
        template.set_image_path(
            'staticimage.logo',
            pkg_resources.resource_filename(
                'py3o.template',
                'tests/templates/images/new_logo.png'
            )
        )

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

        # if you are using python 2.x you should use xrange
        for i in range(1000):
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
        error = False
        try:
            template.render(data)
        except ValueError as e:
            print('The template did not render properly...')
            traceback.print_exc()
            error = True

        assert error is False

    def test_list_duplicate(self):
        """test duplicated listed get a unique id"""
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_list_template.odt'
        )
        outname = get_secure_filename()

        template = Template(template_name, outname)

        class Item(object):
            def __init__(self, val):
                self.val = val
        data_dict = {
            "items": [Item(1), Item(2), Item(3), Item(4)]
        }

        error = False

        template.set_image_path(
            'staticimage.logo',
            pkg_resources.resource_filename(
                'py3o.template',
                'tests/templates/images/new_logo.png'
            )
        )
        template.render(data_dict)

        outodt = zipfile.ZipFile(outname, 'r')
        try:
            content_list = [
                lxml.etree.parse(BytesIO(outodt.read(filename)))
                for filename in template.templated_files
            ]
        except lxml.etree.XMLSyntaxError as e:
            error = True
            print(
                "List was not deduplicated->{}".format(e)
            )

        # remove end file
        os.unlink(outname)

        assert error is False

        # first content is the content.xml
        content = content_list[0]
        list_expr = '//text:list'
        list_items = content.xpath(
            list_expr,
            namespaces=template.namespaces
        )
        ids = []
        for list_item in list_items:
            ids.append(
                list_item.get(
                    '{}id'.format(XML_NS)
                )
            )
        assert ids, "this list of ids should not be empty"
        assert len(ids) == len(set(ids)), "all ids should have been unique"

    def test_missing_opening(self):
        """test orphaned /for raises a TemplateException"""
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_missing_open_template.odt'
        )
        outname = get_secure_filename()
        try:
            template = Template(template_name, outname)

        finally:
            os.remove(outname)

        class Item(object):
            def __init__(self, val):
                self.val = val
        data_dict = {
            "items": [Item(1), Item(2), Item(3), Item(4)]
        }

        template.set_image_path(
            'staticimage.logo',
            pkg_resources.resource_filename(
                'py3o.template',
                'tests/templates/images/new_logo.png'
            )
        )
        # this will raise a TemplateException... or the test will fail
        error_occured = False
        try:
            template.render(data_dict)

        except TemplateException as e:
            error_occured = True
            # make sure this is the correct TemplateException that pops
            assert e.message == "No open instruction for /for"

        # and make sure we raised
        assert error_occured is True

    def test_ignore_undefined_variables_logo(self):

        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_logo.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)

        data = {}

        error = True
        try:
            template.render(data)
            print("Error: template contains a logo variable that must be "
                  "replaced")
        except ValueError:
            error = False

        assert error is False

        template = Template(template_name, outname,
                            ignore_undefined_variables=True)

        error = False
        try:
            template.render(data)
        except:
            traceback.print_exc()
            error = True

        assert error is False

    def test_ignore_undefined_variables_1(self):

        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_undefined_variables_1.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)

        data = {}

        error = True
        try:
            template.render(data)
            print("Error: template contains variables that must be "
                  "replaced")
        except TemplateError:
            error = False

        assert error is False

        template = Template(template_name, outname,
                            ignore_undefined_variables=True)

        error = False
        try:
            template.render(data)
        except:
            traceback.print_exc()
            error = True

        assert error is False

    def test_ignore_undefined_variables_2(self):
        """
        Test ignore undefined variables for template with dotted variables like
        py3o.document.value
        """

        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_undefined_variables_2.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)

        data = {}

        error = True
        try:
            template.render(data)
            print("Error: template contains variables that must be "
                  "replaced")
        except TemplateError:
            error = False

        assert error is False

        template = Template(template_name, outname,
                            ignore_undefined_variables=True)

        error = True
        try:
            template.render(data)
            print("Error: template contains dotted variables that must be "
                  "replaced")
        except TemplateError:
            error = False

        assert error is False

    def test_invalid_template_1(self):
        """a template should not try to define a /for and a for on the same
        paragraph
        """

        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_example_invalid_template.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)

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

        # if you are using python 2.x you should use xrange
        for i in range(1000):
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

        data = dict(
            items=items,
            items2=copy.copy(items),
            document=document
        )

        error = False
        try:
            template.render(data)
        except TemplateException:
            error = True

        assert error is True, "This template should have been refused"

    def test_template_with_function_call(self):
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_template_function_call.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)

        data_dict = {
            'amount': 32.123,
        }

        template.render(data_dict)
        outodt = zipfile.ZipFile(outname, 'r')

        content_list = lxml.etree.parse(
            BytesIO(outodt.read(template.templated_files[0]))
        )

        result_a = lxml.etree.tostring(
            content_list,
            pretty_print=True,
        ).decode('utf-8')

        result_e = open(
            pkg_resources.resource_filename(
                'py3o.template',
                'tests/templates/template_with_function_call_result.xml'
            )
        ).read()

        result_a = result_a.replace("\n", "").replace(" ", "")
        result_e = result_e.replace("\n", "").replace(" ", "")

        assert result_a == result_e

    def test_format_date(self):
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_template_format_date.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)

        data_dict = {
            'datestring': '2015-08-02',
            'datetimestring': '2015-08-02 17:05:06',
            'datestring2': '2015-10-15',
            'datetime': datetime.datetime.strptime(
                '2015-11-13 17:00:20',
                '%Y-%m-%d %H:%M:%S'
            ),
        }

        template.render(data_dict)
        outodt = zipfile.ZipFile(outname, 'r')

        content_list = lxml.etree.parse(
            BytesIO(outodt.read(template.templated_files[0]))
        )

        result_a = lxml.etree.tostring(
            content_list,
            pretty_print=True,
        ).decode('utf-8')

        result_e = open(
            pkg_resources.resource_filename(
                'py3o.template',
                'tests/templates/template_format_date_result.xml'
            )
        ).read()

        result_a = result_a.replace("\n", "").replace(" ", "")
        result_e = result_e.replace("\n", "").replace(" ", "")

        assert result_a == result_e

    def test_format_date_exception(self):
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_template_format_date_exception.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)

        data_dict = {
            'date': '2015/08/02',
        }

        # this will raise a TemplateException... or the test will fail
        error_occured = False
        try:
            template.render(data_dict)

        except TemplateException as e:
            error_occured = True

        # and make sure we raised
        assert error_occured is True

    def test_style_application_with_function_call(self):
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/style_application_with_function_call.odt'
        )

        outname = get_secure_filename()

        template = Template(template_name, outname)

        data_dict = {
            'date': '2015-08-02',
        }

        template.render(data_dict)
        outodt = zipfile.ZipFile(outname, 'r')

        content_list = lxml.etree.parse(
            BytesIO(outodt.read(template.templated_files[0]))
        )

        result_a = lxml.etree.tostring(
            content_list,
            pretty_print=True,
        ).decode('utf-8')

        result_e = open(
            pkg_resources.resource_filename(
                'py3o.template', (
                    'tests/templates/'
                    'style_application_with_function_call_result.xml'
                )
            )
        ).read()

        result_a = result_a.replace("\n", "").replace(" ", "")
        result_e = result_e.replace("\n", "").replace(" ", "")

        assert result_a == result_e

    def test_image_injection(self):
        """Test insertion of images from the data source into the template"""

        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_image_injection.odt'
        )
        logo_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/images/new_logo.png'
        )
        image_names = [
            pkg_resources.resource_filename(
                'py3o.template',
                'tests/templates/images/image{i}.png'.format(i=i)
            ) for i in range(1, 4)
        ]
        outname = get_secure_filename()

        template = Template(template_name, outname)
        logo = open(logo_name, 'rb').read()
        images = [open(iname, 'rb').read() for iname in image_names]

        data_dict = {
            'items': [
                Mock(val1=i, val3=i ** 2, image=base64.b64encode(image))
                for i, image in enumerate(images, start=1)
            ],
            'document': Mock(total=6),
            'logo': logo,
        }

        template.render(data_dict)
        outodt = zipfile.ZipFile(outname, 'r')

        content_list = lxml.etree.parse(
            BytesIO(outodt.read(template.templated_files[0]))
        )
        namelist = outodt.namelist()

        i = 0
        nmspc = template.namespaces
        table = content_list.find('//table:table', nmspc)
        frame_path = 'table:table-cell/text:p/draw:frame'
        for row in table.findall('table:table-row', nmspc):

            frame_elem = row.find(frame_path, nmspc)
            if frame_elem is None:
                continue
            image_elem = frame_elem.find('draw:image', nmspc)
            self.assertIsNotNone(image_elem)

            href = image_elem.get('{{{}}}href'.format(nmspc['xlink']))
            self.assertTrue(href)
            self.assertIn(href, namelist)
            self.assertEqual(images[i], outodt.read(href))

            frame_elem.remove(image_elem)
            i += 1

        self.assertEqual(i, 3, u"Images were not found in the output")

        expected_xml = lxml.etree.parse(
            pkg_resources.resource_filename(
                'py3o.template',
                'tests/templates/image_injection_result.xml'
            )
        )
        result = lxml.etree.tostring(
            content_list, pretty_print=True,
        ).decode('utf-8')
        expected = lxml.etree.tostring(
            expected_xml, pretty_print=True,
        ).decode('utf-8')
        result = result.replace("\n", "").replace(" ", "")
        expected = expected.replace("\n", "").replace(" ", "")

        self.assertEqual(result, expected)

    def test_ignore_undefined_variables_image_injection(self):
        """Test ignore undefined variables for injected image"""

        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_image_injection.odt'
        )

        outname = get_secure_filename()

        data = {
            'items': [],
            'document': Mock(total=6),
        }

        template = Template(template_name, outname)
        error = True
        try:
            template.render(data)
            print("Error: template contains variables that must be "
                  "replaced")
        except TemplateError:
            error = False

        self.assertFalse(error)

        template = Template(
            template_name, outname, ignore_undefined_variables=True
        )
        error = False
        try:
            template.render(data)
        except:
            traceback.print_exc()
            error = True

        self.assertFalse(error)

    def test_text_template(self):

        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_text_template'
        )

        user_data = {'mylist': [
            Mock(var0=1, var1='1', var2=1.0),
            Mock(var0=2, var1='2', var2=2.0),
            Mock(var0=3, var1='3', var2=3.0),
        ]}

        outname = get_secure_filename()

        template = TextTemplate(template_name, outname)
        template.render(user_data)
        result = open(outname, 'rb').read()

        expected = u''.join(
            u'{} {} {}\n'.format(line.var0, line.var1, line.var2)
            for line in user_data['mylist']
        ).encode('utf-8')

        self.assertEqual(result, expected)

    def test_ignore_undefined_variables_text_template(self):

        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_text_template'
        )

        user_data = {}

        outname = get_secure_filename()

        template = TextTemplate(template_name, outname)
        error = True
        try:
            template.render(user_data)
            print("Error: template contains variables that must be "
                  "replaced")
        except TemplateError:
            error = False

        self.assertFalse(error)

        template = TextTemplate(
            template_name, outname, ignore_undefined_variables=True
        )
        error = False
        try:
            template.render(user_data)
        except:
            traceback.print_exc()
            error = True

        self.assertFalse(error)

    def test_remove_soft_page_breaks(self):
        template_xml = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_soft_page_break.odt'
        )
        outname = get_secure_filename()

        template = Template(template_xml, outname)
        soft_breaks = get_soft_breaks(
            template.content_trees[0], template.namespaces
        )
        self.assertEqual(len(soft_breaks), 2)

        template.remove_soft_breaks()
        soft_breaks = get_soft_breaks(
            template.content_trees[0], template.namespaces
        )
        self.assertEqual(len(soft_breaks), 0)

        template = Template(template_xml, outname)
        soft_breaks = get_soft_breaks(
            template.content_trees[0], template.namespaces
        )
        self.assertEqual(len(soft_breaks), 2)

        template.render(data={"list1": [1, 2, 3]})
        soft_breaks = get_soft_breaks(
            template.content_trees[0], template.namespaces
        )
        self.assertEqual(len(soft_breaks), 0)

        outodt = zipfile.ZipFile(outname, 'r')
        content_list = lxml.etree.parse(
            BytesIO(outodt.read(template.templated_files[0]))
        )

        nmspc = template.namespaces
        paragraphs = content_list.findall('//text:p', nmspc)
        bottom_break_paragraphs, middle_break_paragraphs = 0, 0
        for p in paragraphs:
            if not p.text:
                continue
            text = p.text.strip()
            if text == (
                u"This is a text with a margin at the bottom and a "
                u"soft-page-break"
            ):
                bottom_break_paragraphs += 1
            elif text == (
                u"This is a paragraph that is cut in half by a "
                u"soft-page-break. This text should not remain cut "
                u"in half after rendering."
            ):
                middle_break_paragraphs += 1
            else:
                self.fail(u"Unidentified text in result: {}".format(text))

        self.assertEqual(bottom_break_paragraphs, 3)
        self.assertEqual(middle_break_paragraphs, 3)

    def test_remove_soft_breaks_without_tail(self):
        template_xml = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_page_break_without_tail.odt'
        )
        t = Template(template_xml, get_secure_filename())
        soft_breaks = get_soft_breaks(t.content_trees[0], t.namespaces)
        assert len(soft_breaks) > 0

        t.remove_soft_breaks()
        soft_breaks = get_soft_breaks(t.content_trees[0], t.namespaces)
        assert len(soft_breaks) == 0

        t = Template(template_xml, get_secure_filename())
        soft_breaks = get_soft_breaks(t.content_trees[0], t.namespaces)
        assert len(soft_breaks) > 0

        t.render(data={"items": [
            {'Amount': 3, 'Currency': 'D'},
            {'Amount': 2, 'Currency': 'E'},
            {'Amount': 1, 'Currency': 'C'},
        ]})
        soft_breaks = get_soft_breaks(t.content_trees[0], t.namespaces)
        assert len(soft_breaks) == 0

    def test_invalid_links(self):
        u"""Check that exceptions are raised on link url and text mismatch"""

        templates = [
            ('py3o_invalid_link.odt', 'url and text do not match.*'),
            ('py3o_invalid_link_old.odt', 'url and text do not match.*'),
            ('py3o_invalid_link_none.odt', 'Link text not found'),
        ]

        for template, error in templates:
            template_fname = pkg_resources.resource_filename(
                'py3o.template', 'tests/templates/{}'.format(template)
            )
            t = Template(template_fname, get_secure_filename())
            with self.assertRaisesRegexp(TemplateException, error):
                t.render({'amount': 0.0})

    def test_table_cell_function_call(self):
        u"""Test function calls inside ODT table cells"""
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_table_cell_function_call.odt'
        )
        outname = get_secure_filename()
        template = Template(template_name, outname)

        data_dict = {
            'items': [
                Mock(val1=i, val2=range(i), val3=i ** 2)
                for i in range(1, 4)
                ],
            'document': Mock(total=6),
        }

        template.render(data_dict)

    def test_table_cell_for_loop(self):
        u"""Test for loop inside ODT table cells"""
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_table_cell_for_loop.odt'
        )
        outname = get_secure_filename()
        template = Template(template_name, outname)

        data_dict = {
            'items': [
                Mock(val1=i, val2=range(i), val3=i ** 2)
                for i in range(1, 4)
            ],
            'document': Mock(total=6),
        }

        template.render(data_dict)

    def test_odt_value_styles(self):
        u"""Test odt_value attribute and ODF styles"""
        template_name = pkg_resources.resource_filename(
            'py3o.template',
            'tests/templates/py3o_odt_value_styles.odt'
        )
        outname = get_secure_filename()
        template = Template(template_name, outname)

        data_dict = {
            'string_date': '1999-12-30',
            'odt_value_date': Mock(
                __str__=lambda s: '2009-07-06',
                odt_value=40000,
                odt_type='date',
            )
        }

        template.render(data_dict)
        outodt = zipfile.ZipFile(outname, 'r')
        content_list = lxml.etree.parse(
            BytesIO(outodt.read(template.templated_files[0]))
        )

        expected_xml = lxml.etree.parse(
            pkg_resources.resource_filename(
                'py3o.template',
                'tests/templates/odt_value_styles_result.xml'
            )
        )
        result = lxml.etree.tostring(
            content_list, pretty_print=True,
        ).decode('utf-8')
        expected = lxml.etree.tostring(
            expected_xml, pretty_print=True,
        ).decode('utf-8')
        result = result.replace("\n", "").replace(" ", "")
        expected = expected.replace("\n", "").replace(" ", "")

        self.assertEqual(result, expected)
