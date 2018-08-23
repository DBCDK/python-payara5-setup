import fnmatch
from typing import Callable
from xml.etree.ElementTree import Element

from xmltools.manipulation import XmlManipulator


def xpath_of(tag: str, attr: dict = dict()) -> str:
    if attr:
        return tag + "".join(["[@" + x[0] + "=\"" + x[1] + "\"]" for x in attr.items()])
    return tag


class DomainXml(object):
    """"""

    def __init__(self, location: str):
        """
        Load a 'domain.xml' from the given location

        :param location: path od domain.xml file
        """
        self._location = location
        with open(location, "r") as io:
            content = io.read()
            self._xml = XmlManipulator(content)

    def save(self, location: str = None):
        """
        Save the domain.xml to the location from where it was read, or from a newly
        specified location

        :param location:
        :return: None
        """
        if location is None:
            location = self._location
        with open(location, "w") as io:
            content = self._xml.to_xml()
            io.write(content)

    def _ensure(self, xpath: str, tag: str, attrs: dict = None) -> Element:
        if attrs is None:
            attrs = dict()
        root = self._xml.root(xpath)
        xp = xpath_of(tag, attrs)
        if root.has(xp):
            return root.append_at(xp)
        return root.append_at(".").element(tag, attrs)

    def app(self, name: str, path: str, context_root: str = "/"):
        """
        Setup an application under the name 'name' with a app file from 'path'
        ensure cdi-service is enabled
        :param name:
        :param path:
        :param context_root:
        :return: None
        """
        self._ensure(".", "applications")
        self._ensure('applications', "application", {"name": name}) \
            .clear() \
            .attr("name", name) \
            .attr("location", "file://" + path) \
            .attr("context-root", context_root) \
            .attr("object-type", "user") \
            .element("property", {"name": "cdiDevModeEnabled", "value": "false"}).done() \
            .element("property", {"name": "implicitCdiEnabled", "value": "true"}).done() \
            .element("property", {"name": "preserveAppScopedResources", "value": "false"}).done() \
            .element("module", {"name": name}) \
            .element("engine", {"sniffer": "cdi"}).done() \
            .element("engine", {"sniffer": "ejb"}).done() \
            .element("engine", {"sniffer": "security"}).done() \
            .element("engine", {"sniffer": "web"}).done() \
            .element("engine", {"sniffer": "webservices"}).done() \
            .done()
        self._ensure('servers/server[@name="server"]', "application-ref", {"ref": name, "virtual-servers": "server"})
        self._ensure('configs/config[@name="server-config"]', "cdi-service")

    def osgi(self, name: str, path: str):
        """
        Setup an application under the name 'name' with a app file from 'path'
        ensure cdi-service is enabled
        :param name:
        :param path:
        :return: None
        """
        self._ensure(".", "applications")
        self._ensure('applications', "application", {"name": name}) \
            .clear() \
            .attr("name", name) \
            .attr("location", "file://" + path) \
            .attr("object-type", "user") \
            .element("property", {"name": "archiveType", "value": "osgi"}).done() \
            .element("property", {"name": "isComposite", "value": "true"}).done() \
            .element("module", {"name": name}) \
            .element("engine", {"sniffer": "osgi"}).done() \
            .done()
        self._ensure('servers/server[@name="server"]', "application-ref", {"ref": name, "virtual-servers": "server"})

    def custom_resource_primitive(self, type: str, name: str, value: str) -> None:
        """
        Create a custom resource of a primitive

        :param type: type 'java.lang.*'
        :param name: jndi name
        :param value: content
        :return: None
        """
        p = self._ensure('resources', "custom-resource", {"jndi-name": name}) \
            .attr("factory-class", "org.glassfish.resources.custom.factory.PrimitivesAndStringFactory") \
            .attr("res-type", type) \
            .element("property", {"name": "value", "value": value})
        self._ensure('servers/server[@name="server"]', "resource-ref", {"ref": name})

    def custom_resource_props(self, name: str, props: dict) -> None:
        """
        Create a custom resource of java.lang.Properties type

        :param name: jndi-name
        :param props: key/value pairs
        :return: None
        """
        p = self._ensure('resources', "custom-resource", {"jndi-name": name}) \
            .attr("factory-class", "org.glassfish.resources.custom.factory.PropertiesFactory") \
            .attr("res-type", "java.util.Properties")
        for kv in props.items():
            p.element("property", {"name": kv[0], "value": kv[1]})
        self._ensure('servers/server[@name="server"]', "resource-ref", {"ref": name})

    def props_at(self, xpath: str, props: dict) -> None:
        """
        Add key/value props <property name="key" value="value"/> at a given xpath

        :param xpath: location where properties should be set
        :param props: key/value pairs
        :return: None
        """
        points = [point for point in self._xml.append_at_all(xpath)]
        for point in points:
            for kv in props.items():
                point.element("property", {"name": kv[0], "value": kv[1]})

    def attrs_at(self, xpath: str, attrs: dict) -> None:
        """
        Add key/value props key="value" at a given xpath (element)

        :param xpath: location where properties should be set
        :param props: key/value pairs
        :return: None
        """
        for p in self._xml.append_at_all(xpath):
            for kv in attrs.items():
                p.attr(kv[0], kv[1])

    def ensure_at(self, xpath: str, attrs: dict) -> None:
        """
        Add a new element at a given xpath (element)

        :param xpath: location where element should be added
        :param props: key/value pairs (. = tag-name)
        :return: None
        """

        tag = attrs['.']
        del attrs['.']
        self._ensure(xpath, tag, attrs)

    def system_property(self, key: str, value: str,) -> None:
        self._ensure('servers/server[@name="server"]', 'system-property', {"name": key}) \
            .attr("value", value)


    def jdbc_resource(self, name: str, attribs: dict, props: dict) -> None:
        """
        Creata a jdbc pool and resource at a given jndi-path

        :param name: base-jndi-name
        :param attribs: pool attributes
        :param props: pool resources
        :return: None
        """
        p = self._ensure('resources', 'jdbc-connection-pool', {'name': name + "/pool"})
        p.clear()
        p.attr('name', name + "/pool")
        for pair in attribs.items():
            p.attr(pair[0], pair[1])
        for pair in props.items():
            p.element('property', {'name': pair[0], 'value': pair[1]})
        self._ensure('resources', "jdbc-resource", {"jndi-name": name}) \
            .attr('pool-name', name + "/pool")
        self._ensure('servers/server[@name="server"]', "resource-ref", {"ref": name})

    def jms_remote(self, addr: str) -> None:
        """
        Set default up jms to to a remote host

        :param addr: address of host
        :return: None
        """
        p = self._ensure('configs/config[@name="server-config"]', 'jms-service')
        p.attr("default-jms-host", "default_JMS_host")
        p.attr("type", "REMOTE")
        a = p.element("jms-host") \
            .attr("name", "default_JMS_host")
        if ':' in addr:
            (host, port) = addr.split(":", 1)
            a.attr("host", host)
            a.attr("port", port)
        else:
            a.attr("host", addr)

    def jms_factory_resource(self, name: str, attribs: dict, props: dict) -> None:
        """
        Create a jms factory

        :param name: jndi-name of factory
        :param attribs: factory attributes
        :param props: factory attributes
        :return: None
        """
        pool_name = name + "-Connection-Pool"
        p = self._ensure('resources', 'connector-connection-pool', {'name': pool_name})
        p.clear()
        p.attr('name', pool_name)
        for pair in attribs.items():
            p.attr(pair[0], pair[1])
        for pair in props.items():
            p.element('property', {'name': pair[0], 'value': pair[1]})
        p = self._ensure('resources', 'connector-resource', {"jndi-name": name})
        p.clear()
        p.attr("jndi-name", name)
        p.attr("pool-name", pool_name)
        self._ensure('servers/server[@name="server"]', "resource-ref", {"ref": name})

    def jms_destination_resource(self, name: str, attribs: dict, props: dict) -> None:
        """
        Create a Topic/Queue

        :param name: jndi-name
        :param attribs: destination attributes
        :param props: destination properties
        :return:
        """
        p = self._ensure('resources', "admin-object-resource", {'jndi-name': name})
        p.clear()
        p.attr('jndi-name', name)
        for pair in attribs.items():
            p.attr(pair[0], pair[1])
        for pair in props.items():
            p.element('property', {'name': pair[0], 'value': pair[1]})
        self._ensure('servers/server[@name="server"]', "resource-ref", {"ref": name})

    def jvm_options(self, clear: bool, adds: set, removes: set) -> None:

        if clear:
            self._xml.remove('configs/config[@name="server-config"]/java-config/jvm-options')
        else:
            if removes:
                self._xml.iterate('configs/config[@name="server-config"]/java-config',
                                  self._jvm_filter(removes))
        p = self._xml.append_at('configs/config[@name="server-config"]/java-config')
        for add in adds:
            p.element("jvm-options").text(add)

    @staticmethod
    def _jvm_filter(removes: set) -> Callable[[Element, Element], bool]:
        def func(node, parent):
            for remove in removes:
                if fnmatch.fnmatchcase(node.text, remove):
                    parent.remove(node)
                    return True
            return False

        return func

    @property
    def xml(self):
        return self._xml
