from django.test import TestCase
from django.template.loader import render_to_string
from django.template.base import TemplateDoesNotExist
from override.templatetags.override_tags import OverrideError


class RenderTest(TestCase):
    """docstring for SimpleTest"""
    def testTwoFilesystem(self):
        self.assertEqual(render_to_string("normal.html"), u'This is a normal Template.\n\n\nOverride block1\n')

    def testOneFileSystemOneAppDirectory(self):
        self.assertEqual(render_to_string("app.html"), u'This is a normal Template.\n\n\nOverride block1\n')

    def testTwoAppDirectories(self):
        self.assertEqual(render_to_string("app2.html"), u'This is a normal Template.\n\n\nOverride block1\n')

    def testMultipleOverride(self):
        self.assertEqual(render_to_string("app3.html"), u'This is a normal Template.\n\n\nOverride block1 again\n')

    def testOverrideAndExtends(self):
        self.assertEqual(render_to_string("override_extends.html"), u'This is a normal Template.\n\n\nOverride block1 again\n')


class ExceptionTest(TestCase):
    """docstring for ExceptionTest"""
    def testNoBaseTemplate(self):
        self.assertRaises(OverrideError, render_to_string, "nobase.html")

    def testNameError(self):
        self.assertRaises(OverrideError, render_to_string, "name_difference.html")

    def testNoExistTemplate(self):
        self.assertRaises(TemplateDoesNotExist, render_to_string, "noexist.html")
