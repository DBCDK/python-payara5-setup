from unittest import TestCase

from xmltools.manipulation import XmlManipulator

xml_1 = """<?xml version="1.0"?>
<root><foo><bar/></foo></root>"""
xml_2 = """<?xml version="1.0"?>
<ns1:root xmlns:ns1="info:1"><ns1:foo><ns1:bar/><ns1:bar a="b&apos;"/></ns1:foo></ns1:root>"""
xml_3 = """<?xml version="1.0"?>
<ns1:root xmlns:ns1="info:1"><ns1:foo> <ns1:bar a="1"/> <ns1:bar a="2"/> </ns1:foo></ns1:root>"""


class XmlTestCase(TestCase):
    def assertInOrder(self, text, *args):
        try:
            pos = -1
            for arg in args:
                p1 = text.index(arg)
                if p1 < pos:
                    self.fail("unexpected order regarding: " + arg + " in: " + text)
                pos = p1
            return None
        except ValueError as e:
            self.fail("missing substring: " + arg + " in: " + text)


class TestXmlManipulator(XmlTestCase):

    def test_remove(self):
        x = XmlManipulator(xml_1)
        x.remove("./foo/bar")
        self.assertNotIn("bar", x.to_xml())
        self.assertInOrder(x.to_xml(), "root", "foo", "/root")

    def test_remove_ns(self):
        x = XmlManipulator(xml_2)
        x.add_namespace("ns2", "info:1")
        x.remove("./ns2:foo/ns2:bar")
        self.assertNotIn("bar", x.to_xml())
        self.assertInOrder(x.to_xml(), "ns0:root", "ns0:foo", "/ns0:root")

    def test_remove_attr_ns(self):
        x = XmlManipulator(xml_2)
        x.add_namespace("ns2", "info:1")
        x.remove_attr("./ns2:foo/ns2:bar[@a=\"b'\"]", 'a')
        self.assertNotIn("a=", x.to_xml())

    def test_set_attr_ns(self):
        x = XmlManipulator(xml_2)
        x.add_namespace("ns2", "info:1")
        x.set_attr("./ns2:foo/ns2:bar[@a=\"b'\"]", 'k', 'v')
        self.assertIn("k=", x.to_xml())

    def test_replace_ns(self):
        x = XmlManipulator(xml_2)
        x.add_namespace("ns2", "info:1")
        x.replace("./ns2:foo/ns2:bar", "<ns2:xml1/><ns2:xml2/>")
        self.assertInOrder(x.to_xml(), "ns0:root", "ns0:foo", "ns0:xml1", "ns0:xml2", "/ns0:foo", "/ns0:root")

    def test_append_ns(self):
        x = XmlManipulator(xml_2)
        x.add_namespace("ns2", "info:1")
        x.append("./ns2:foo/ns2:bar[@a=\"b'\"]", "<ns2:xml1/><ns2:xml2/>")

    def test_has_yes(self):
        x = XmlManipulator(xml_2)
        x.add_namespace("ns2", "info:1")
        self.assertTrue(x.has("ns2:foo/ns2:bar"))

    def test_has_no(self):
        x = XmlManipulator(xml_2)
        x.add_namespace("ns2", "info:1")
        self.assertFalse(x.has("./ns2:fool/ns2:bar"))

    def test_append_at(self):
        x = XmlManipulator(xml_2)
        x.add_namespace("ns2", "info:1")
        p = x.append_at(".")
        p.element("fool").text("'s name").element("barley", namespace="ns2").attr("a", "b")
        self.assertInOrder(x.to_xml(), "ns0:root", "ns0:foo", "ns0:bar", "/ns0:foo", "fool", "name", "ns0:barley", 'a="b"', "/fool", "/ns0:root")

    def test_root(self):
        x = XmlManipulator(xml_2)
        x.add_namespace("ns2", "info:1")
        r = x.root("ns2:foo")
        r.append_at("ns2:bar").text("here")
        self.assertInOrder(x.to_xml(), "ns0:root", "ns0:foo", "ns0:bar", "here", "/ns0:bar", "/ns0:foo", "/ns0:root")

    def test_iterate(self):
        x = XmlManipulator(xml_3)
        x.add_namespace("ns2", "info:1")
        l = []
        x.iterate("ns2:foo", lambda e, p: l.append(e.get("a")))
        self.assertIn("1", l)
        self.assertIn("2", l)
