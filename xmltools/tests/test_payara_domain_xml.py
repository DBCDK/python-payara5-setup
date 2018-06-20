import hashlib
import os
from unittest import TestCase

from xmltools.manipulation import XmlManipulator
from xmltools.payara_domain_xml import DomainXml

if os.path.isdir(os.path.join("xmltools", "tests")):
    os.chdir(os.path.join("xmltools", "tests"))


class XmlTestCase(TestCase):
    def assertInOrder(self, domain_xml, *args):
        text = domain_xml._xml.to_xml()
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


def md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class TestDomainXml(XmlTestCase):

    def test_foo(self):
        domain_xml = DomainXml("domain_orig.xml")
        domain_xml.save("domain2.xml")
        domain_xml.save("domain3.xml")
        md5_old = md5("domain2.xml")
        md5_new = md5("domain3.xml")
        self.assertEqual(md5_old, md5_new)

    def test_ensure(self):
        domain_xml = DomainXml("domain_orig.xml")
        domain_xml._ensure('servers/server[@name="server"]', "application-ref", {"ref": "app", "virtual-servers": "server"})
        self.assertInOrder(domain_xml, "<servers>", "<server", "<application-ref", "ref=\"app\"", "</server>", "</servers>")

        domain_xml.save("domain2.xml")
        md5_old = md5("domain2.xml")
        domain_xml._ensure('servers/server[@name="server"]', "application-ref", {"ref": "app", "virtual-servers": "server"})
        domain_xml.save("domain3.xml")
        md5_new = md5("domain3.xml")
        self.assertEqual(md5_old, md5_new)

    def test_ensure_app(self):
        domain_xml = DomainXml("domain_orig.xml")
        domain_xml._ensure('servers/server[@name="server"]', "application-ref", {"ref": "myapp", "virtual-servers": "server"})
        domain_xml._ensure('configs/config[@name="server-config"]', "cdi-service")
        domain_xml._ensure(".", "applications")
        domain_xml._ensure('applications', "application", {"name": "myapp"}) \
            .clear() \
            .attr("name", "myapp") \
            .attr("location", "file:///home/bogeskov/NetBeansProjects/decorator/mini/target/mini-1.0-SNAPSHOT.war") \
            .attr("context-root", "/") \
            .attr("object-type", "user") \
            .element("property", {"name": "cdiDevModeEnabled", "value": "false"}).done() \
            .element("property", {"name": "implicitCdiEnabled", "value": "true"}).done() \
            .element("property", {"name": "preserveAppScopedResources", "value": "false"}).done() \
            .element("module", {"name": "mini"}) \
            .element("engine", {"sniffer": "cdi"}).done() \
            .element("engine", {"sniffer": "ejb"}).done() \
            .element("engine", {"sniffer": "security"}).done() \
            .element("engine", {"sniffer": "web"}).done() \
            .done()
        domain_xml.save("domain.xml")

        text = domain_xml._xml.to_xml()
        print(text)
