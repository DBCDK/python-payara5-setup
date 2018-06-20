from io import BytesIO
from typing import TypeVar, Callable
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment

from xml.sax.saxutils import quoteattr


class XmlManipulator(object):

    def __init__(self, content:TypeVar('xml', str, Element), namespaces: dict = dict()):
        if type(content) is str:
            self._root = ET.fromstring(content)
        else:
            self._root = content
        self._namespaces = namespaces
        self._build_parent_map()

    def ns(self, tag, namespace):
        if namespace is None:
            return tag
        return "{" + self._namespaces[namespace] + "}" + tag

    def _build_parent_map(self):
        self._parent = {c: p for p in self._root.iter() for c in p}

    def to_xml(self) -> str:
        out = BytesIO()
        ET.ElementTree(self._root).write(out, encoding="UTF-8", xml_declaration=True)
        return out.getvalue().decode("UTF-8")

    def add_namespace(self, prefix, uri):
        self._namespaces[prefix] = uri

    def remove(self, xpath: str) -> bool:
        modified = False
        for node in self._root.findall(xpath, namespaces=self._namespaces):
            self._parent[node].remove(node)
            modified = True
        if modified:
            self._build_parent_map()
        return modified

    def remove_attr(self, xpath: str, attr: str) -> bool:
        modified = False
        for node in self._root.findall(xpath, namespaces=self._namespaces):
            if attr in node.attrib:
                node.attrib.pop(attr)
        return modified

    def set_attr(self, xpath: str, attr: str, value: str) -> bool:
        modified = False
        for node in self._root.findall(xpath, namespaces=self._namespaces):
            node.set(attr, value)
        return modified

    def replace(self, xpath: str, content: str) -> bool:
        modified = False
        sub_nodes = self._text_to_nodes(content)
        for node in self._root.findall(xpath, namespaces=self._namespaces):
            parent = self._parent[node]
            if sub_nodes is not None:
                index = parent.getchildren().index(node)
                for sub_node in sub_nodes:
                    index = index + 1
                    parent.insert(index, sub_node)
                sub_nodes = None
            parent.remove(node)
            modified = True
        if modified:
            self._build_parent_map()
        return modified

    def append(self, xpath: str, content: str) -> bool:
        xml = ("<xml" +
               "".join([" xmlns:%s=%s" % (k, quoteattr(self._namespaces[k])) for k in self._namespaces]) +
               ">" + content + "</xml>")
        sub_nodes = self._text_to_nodes(content)
        for node in self._root.findall(xpath, namespaces=self._namespaces):
            for sub_node in sub_nodes:
                node.append(sub_node)
            self._build_parent_map()
            return True
        return False

    def append_at(self, xpath: str) -> TypeVar('XmlPoint'):
        node = self._root.find(xpath, namespaces=self._namespaces)
        if node is None:
            raise Exception("Node not found")
        return XmlPoint(node, self)

    def append_at_all(self, xpath: str) -> TypeVar('XmlPoint'):
        nodes = self._root.findall(xpath, namespaces=self._namespaces)
        if nodes is None or len(nodes) == 0:
            raise Exception("Node not found")
        return [XmlPoint(node, self) for node in nodes]

    def has(self, xpath: str) -> bool:
        return self._root.find(xpath, namespaces=self._namespaces) is not None

    def root(self, xpath: str) -> TypeVar('XmlManipulator'):
        node = self._root.find(xpath, namespaces=self._namespaces)
        if node is None:
            raise Exception("Could not find root: " + xpath)
        return XmlManipulator(node, self._namespaces)

    def iterate(self, xpath: str, cb: Callable[[Element, Element], bool]) -> None:
        nodes = self._root.findall(xpath, namespaces=self._namespaces)
        modified = False
        for parent in nodes:
            for child in parent:
                modified = cb(child, parent) or modified
        if modified:
            self._build_parent_map()

    def _text_to_nodes(self, content):
        xml = ("<xml" +
               "".join([" xmlns:%s=%s" % (k, quoteattr(self._namespaces[k])) for k in self._namespaces]) +
               ">" + content + "</xml>")
        return ET.fromstring(xml).getchildren()


class XmlPoint(object):

    def __init__(self, top: Element, xml: TypeVar('XmlManipulator') = None, parent: TypeVar('XmlPoint') = None):
        self._top = top
        self._xml = xml
        self._parent = parent

    def element(self, tag: str, attr: dict = dict(), namespace: str = None) -> TypeVar('XmlPoint'):
        node = SubElement(self._top, self._xml.ns(tag, namespace), attrib=attr)
        self._xml._build_parent_map()
        return XmlPoint(node, self._xml, self)

    def text(self, content: str) -> TypeVar('XmlPoint'):
        self._top.text = content
        return self

    def attr(self, key: str, value: str = None, namespace: str = None) -> TypeVar('XmlPoint'):
        self._top.set(self._xml.ns(key, namespace), value)
        return self

    def clear(self):
        self._top.clear()
        return self

    def done(self):
        return self._parent
