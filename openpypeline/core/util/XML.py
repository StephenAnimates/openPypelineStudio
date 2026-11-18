"""Serialize and deserialize supported Python objects as XML.

Provides a lightweight XML pickling and unpickling utility for primitive types,
collections (``list``, ``tuple``, ``dict``), and custom classes inheriting
from :class:`xmlserialize`.

:File: XML.py
:Original Framework: openPipeline by Kickstand
:License: Common Public License 1.0 (CPL-1.0)

Usage Example::

    from openpypeline.core.util.XML import xmlfile, xmlserialize

    class ProjectConfig(xmlserialize):
        def __init__(self):
            self.name = "DemoProject"
            self.fps = 24

    handler = xmlfile("/tmp/config.xml")
    handler.save(ProjectConfig())
    loaded = handler.load()
"""

import logging
import sys
import xml.dom.minidom
from typing import Any, Callable, Optional
import __main__

#: Module logger for XML serialization and deserialization events.
logger = logging.getLogger("openPypeline.xml")

class xmlserialize:
    """Marker base class for objects encoded by the XML serializer.

    Subclasses can optionally define a ``__pickle_to_xml__`` list of attribute
    names to restrict which attributes are serialized, or implement custom
    ``_xml_encode_<attr>`` and ``_xml_decode_<attr>`` hooks.
    """

class xmlunpicklingException(Exception):
    """Raised when serialized XML has an invalid container structure."""

    pass

class xmlfile:
    """Handle saving and loading an :class:`xmlserialize` object to an XML file.

    :ivar filename: Path to the target XML file on disk.
    :vartype filename: Optional[str]
    """

    def __init__(self, filename: Optional[str] = None) -> None:
        """Store the path used by subsequent XML load and save operations.

        :param filename: File system path to read from or write to.
        """
        self.filename = filename

    def load(self) -> Any:
        """Load XML from :attr:`filename` and deserialize it into a Python object.

        :returns: The reconstructed Python object or data structure.
        :raises xmlunpicklingException: If the XML container layout is malformed.
        """
        node = xml.dom.minidom.parse(self.filename)
        return self.unpickle(node.documentElement)

    def save(self, obj: Any) -> None:
        """Serialize a supported Python object and write it to :attr:`filename`.

        :param obj: The object or primitive data structure to serialize.
        """
        node = self.pickle(root=obj, fabric=xml.dom.minidom.Document())
        with open(self.filename, "w", encoding="utf-8") as f:
            node.writexml(f)

    # helper functions
    def getMod(self, cls: str) -> Optional[Any]:
        """Resolve and instantiate a class from a dotted module path string.

        Searches ``sys.modules`` and ``__main__`` to locate the target module
        and instantiate the requested class.

        :param cls: Dotted class path (for example, ``"module1.module2.MyClass"``).
        :returns: A new instance of the resolved class, or ``None`` if not found.
        """
        if "." not in cls:
            return None

        # separate the module from the class [module1.module2].[cls]
        logger.debug(f"Class: {cls}")
        mod = cls[0 : cls.rindex(".")]
        className = cls[cls.rindex(".") + 1 :]

        # Check sys.modules first for a safer and more direct lookup
        if mod in sys.modules:
            class_obj = getattr(sys.modules[mod], className, None)
            if class_obj:
                return class_obj()

        for d in dir(__main__):
            try:
                module_obj = getattr(__main__, d)
                mod_name = getattr(module_obj, "__name__", None)
                if mod_name and f"{mod_name}.{className}" == cls:
                    class_obj = getattr(module_obj, className)
                    return class_obj()
            except Exception:
                pass  # Ignore if no attribute __name__

        return None

    def getType(self, obj: Any) -> str:
        """Generate an undecorated class name string for an object.

        :param obj: Any Python object instance.
        :returns: The clean type or class path string extracted from ``obj.__class__``.
        """
        return str(obj.__class__).split("'")[1]

    #: Primitive type names serialized directly as XML text nodes.
    _easyToPickle: list[str] = ["int", "float", "str", "unicode", "long"]

    def _isCallable(self, obj: Any) -> bool:
        """Return whether an object can be called like a function.

        :param obj: The object to inspect.
        :returns: ``True`` if ``obj`` defines ``__call__``, otherwise ``False``.
        """
        return hasattr(obj, "__call__")
    #
    #   pickling
    #

    def _pickleDictItems(
        self,
        root: dict[Any, Any],
        node: xml.dom.minidom.Element,
        fabric: xml.dom.minidom.Document,
    ) -> None:
        """Append each dictionary key and value as an XML item node.

        :param root: Dictionary to serialize.
        :param node: Parent XML element receiving the ``item`` nodes.
        :param fabric: Active DOM document used to create XML elements.
        """
        for key, value in root.items():
            tempnode = fabric.createElement("item")
            tempnode.appendChild(self.pickle(key, fabric, "key"))
            tempnode.appendChild(self.pickle(value, fabric, "value"))
            node.appendChild(tempnode)

    def _pickleListItems(
        self,
        root: list[Any] | tuple[Any, ...],
        node: xml.dom.minidom.Element,
        fabric: xml.dom.minidom.Document,
    ) -> None:
        """Append sequence entries as indexed XML item nodes.

        :param root: Sequence (``list`` or ``tuple``) to serialize.
        :param node: Parent XML element receiving the indexed ``item`` nodes.
        :param fabric: Active DOM document used to create XML elements.
        """
        for idx, obj in enumerate(root):
            tempnode = self.pickle(obj, fabric, "item")
            tempnode.attributes["index"] = str(idx)
            node.appendChild(tempnode)

    _pickleTupleItems = _pickleListItems

    def pickle(
        self,
        root: Any,
        fabric: xml.dom.minidom.Document,
        elementName: str = "root",
    ) -> xml.dom.minidom.Element:
        """Serialize a supported Python value into an XML element tree.

        Dispatches serialization based on whether ``root`` is an
        :class:`xmlserialize` instance, a primitive type listed in
        :attr:`_easyToPickle`, a ``dict``, ``list``, or ``tuple``, falling back
        to ``repr(root)`` for unsupported types.

        :param root: Python value or :class:`xmlserialize` instance to encode.
        :param fabric: Active DOM document used to create XML nodes.
        :param elementName: Tag name assigned to the generated XML element.
        :returns: The populated DOM element representing ``root``.
        """
        node = fabric.createElement(elementName)
        typeStr = self.getType(root)
        node.attributes["type"] = typeStr

        if isinstance(root, xmlserialize):
            node = self._pickleObjectWithAttributes(node, root, fabric, elementName)
        elif typeStr in self._easyToPickle:
            node.appendChild(fabric.createTextNode(str(root)))
        elif isinstance(root, dict):
            self._pickleDictItems(root, node, fabric)
        elif isinstance(root, list):
            self._pickleListItems(root, node, fabric)
        elif isinstance(root, tuple):
            self._pickleTupleItems(root, node, fabric)
        else:
            # fallback handler
            node.appendChild(fabric.createTextNode(repr(root)))
        return node

    def _pickleObjectWithAttributes(
        self,
        node: xml.dom.minidom.Element,
        root: xmlserialize,
        fabric: xml.dom.minidom.Document,
        elementName: str,
    ) -> xml.dom.minidom.Element:
        """Pickle object members, prioritizing custom encoding if present.

        Serializes either the attributes listed in ``root.__pickle_to_xml__``
        or all non-dunder, non-callable attributes on ``root``. If a
        ``_xml_encode_<name>`` hook exists on ``root``, its string output is
        stored under a ``type="custom"`` child element.

        :param node: Target XML element representing the serialized object.
        :param root: :class:`xmlserialize` instance whose attributes are encoded.
        :param fabric: Active DOM document used to create child elements.
        :param elementName: Tag name of the parent element.
        :returns: The updated DOM element containing serialized member nodes.
        """
        if hasattr(root, "__pickle_to_xml__"):
            attributesToPickle = root.__pickle_to_xml__
        else:
            # avoid members which are python internal
            attributesToPickle = [
                name for name in dir(root) if not name.startswith("__")
            ]

        for name in attributesToPickle:
            obj = getattr(root, name)

            # do not pickle member functions
            if self._isCallable(obj):
                continue

            # is there some special encoding method ??
            if hasattr(root, f"_xml_encode_{name}"):
                value = getattr(root, f"_xml_encode_{name}")()
                element = fabric.createElement(name)
                element.attributes["type"] = "custom"
                element.appendChild(fabric.createTextNode(value))
                node.appendChild(element)
            else:
                node.appendChild(self.pickle(obj, fabric, name))
        return node
    #
    #   unpickling
    #

    # helper functions

    def _getElementChilds(
        self, node: xml.dom.minidom.Element, doLower: int = 1
    ) -> list[tuple[str, xml.dom.minidom.Element]]:
        """Return a list of ``(tagname, element)`` pairs for child elements.

        :param node: Parent DOM element to inspect.
        :param doLower: If truthy, converts tag names to lowercase.
        :returns: List of ``(tag_name, child_element)`` tuples excluding text nodes.
        """
        dolow: Callable[[str], str] = (
            (lambda x: x.lower()) if doLower else (lambda x: x)
        )
        return [
            (dolow(no.tagName), no)
            for no in node.childNodes
            if no.nodeType != no.TEXT_NODE
        ]

    def _getText(self, nodelist: xml.dom.minidom.NodeList) -> str:
        """Collect and strip text content from text nodes in a node list.

        :param nodelist: DOM node list to extract text from.
        :returns: Concatenated and whitespace-stripped text content.
        """
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc.strip()

    def unpickle(
        self, node: xml.dom.minidom.Element, obj: Optional[Any] = None
    ) -> Any:
        """Deserialize a DOM element back into its original Python object.

        Inspects ``node.attributes["type"]`` to reconstruct primitives listed in
        :attr:`_easyToPickle`, collections (``tuple``, ``list``, ``dict``),
        custom ``_xml_decode_<tag>`` fields, or class instances resolved from
        ``__main__`` or :meth:`getMod`.

        :param node: XML DOM element with a ``type`` attribute.
        :param obj: Optional parent object instance used when invoking custom
            ``_xml_decode_<tag>`` handlers.
        :returns: Reconstructed primitive, collection, or class instance.
        :raises xmlunpicklingException: If a container element is malformed.
        """
        typeName = node.attributes["type"].value

        if typeName in self._easyToPickle:
            initValue = self._getText(node.childNodes)
            types: dict[str, Callable[[str], Any]] = {
                "int": int,
                "float": float,
                "str": str,
                "unicode": str,
                "long": int,
            }
            return types[typeName](initValue)
        elif typeName == "tuple":
            return self._unpickleTuple(node)
        elif typeName == "list":
            return self._unpickleList(node)
        elif typeName == "dict":
            return self._unpickleDict(node)
        elif typeName == "custom":
            fun = f"_xml_decode_{node.tagName}"
            if not obj or not hasattr(obj, fun):
                return ""
            return getattr(obj, fun)(self._getText(node.childNodes))
        else:
            try:
                obj = getattr(__main__, typeName)()
            except Exception:
                obj = self.getMod(typeName)

            for name, element in self._getElementChilds(node):
                obj.__dict__[name] = self.unpickle(element, obj)
            return obj

    def _unpickleList(self, node: xml.dom.minidom.Element) -> list[Any]:
        """Rebuild a list from indexed child elements in serialized XML.

        :param node: XML element representing a serialized ``list`` or ``tuple``.
        :returns: Reordered Python list of deserialized items.
        :raises xmlunpicklingException: If a child tag is not named ``item``.
        """
        li = []
        # collect entries, you can not assume that the members of the list appear in the right order !
        for name, element in self._getElementChilds(node):
            if name != "item":
                raise xmlunpicklingException()
            idx = int(element.attributes["index"].value)
            obj = self.unpickle(element)
            li.append((idx, obj))

        # rebuild list with right order
        li.sort(key=lambda x: x[0])
        return [item[1] for item in li]

    def _unpickleTuple(self, node: xml.dom.minidom.Element) -> tuple[Any, ...]:
        """Rebuild a tuple using the serialized list representation.

        :param node: XML element representing a serialized ``tuple``.
        :returns: Deserialized Python tuple.
        :raises xmlunpicklingException: If a child tag is not named ``item``.
        """
        return tuple(self._unpickleList(node))

    def _unpickleDict(self, node: xml.dom.minidom.Element) -> dict[Any, Any]:
        """Rebuild a dictionary from serialized key-value item elements.

        :param node: XML element representing a serialized ``dict``.
        :returns: Reconstructed Python dictionary.
        :raises xmlunpicklingException: If an entry is not an ``item`` or does not
            contain exactly two child elements (``key`` and ``value``).
        """
        dd = dict()
        for name, element in self._getElementChilds(node):
            if name != "item":
                raise xmlunpicklingException()
            childList = self._getElementChilds(element)
            if len(childList) != 2:
                raise xmlunpicklingException()
            for childName, childElement in childList:
                if childName == "key":
                    key = self.unpickle(childElement)
                elif childName == "value":
                    value = self.unpickle(childElement)
            dd[key] = value
        return dd
