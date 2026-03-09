import logging
import xml.etree.ElementTree as Et
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional, Union
from xml.etree.ElementTree import XMLParser

from ..errors import (
    EmptyFileError,
    InvalidLocaleDocumentError,
    ParseError,
)
from ..utils import _get_locale_code
from .base_loader import BaseLoader


class Parser(Et.TreeBuilder):
    """Custom XML parser to support comments extraction."""

    def comment(self, data: str | None):
        """Handle XML comments by treating them as special nodes in the tree."""
        if not data:
            return

        self.start(Et.Comment, {})
        self.data(data)
        self.end(Et.Comment)  # type: ignore


class XmlLoader(BaseLoader):
    """Loader for XML files."""

    file_extension = ".xml"

    INLINE_TAGS = {
        "b",
        "strong",
        "i",
        "em",
        "mark",
        "small",
        "del",
        "ins",
        "sub",
        "sup",
        "code",
        "kbd",
        "samp",
        "var",
        "u",
        "s",
        "q",
        "span",
        "br",
        "link",
        "img",
    }

    def __init__(self, strict: bool = False):
        """Initialize the XmlLoader class."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._strict = strict
        self._root_tags: Dict[str, str] = {}
        self._explicit_lists: Dict[str, Dict[str, str]] = {}

    def load(self, filepath: Union[str, Path]) -> Optional[Union[Dict, List[dict]]]:
        """Load and processes localization data from an XML file."""
        filepath = Path(filepath)
        filename = filepath.name

        try:
            tree = Et.parse(filepath)
            root = tree.getroot()
            multiple = root.tag in ("locales", "localizations", "translations")
            locale_code = "" if multiple else _get_locale_code(filename)
            data = self._etree_to_dict(root, locale_code)
            if not data:
                return self._throw(f"Locale file '{filename}' is empty", EmptyFileError)

            if multiple:
                if not isinstance(data, dict):
                    return self._throw(
                        f"File '{filename}': multiple locales expected, but got {type(data).__name__}",
                        InvalidLocaleDocumentError,
                    )

                processed = []
                for loc_code, translations in data.items():
                    if loc_code.startswith("comment_"):
                        continue

                    if not isinstance(translations, dict):
                        return self._throw(
                            f"File '{filename}': locale '{loc_code}': data must be a dict, "
                            f"got {type(translations).__name__}",
                            InvalidLocaleDocumentError,
                        )

                    self._root_tags[loc_code] = root.tag
                    processed.append({"locale": loc_code, **translations})

                return processed

            if not isinstance(data, dict):
                return self._throw(
                    f"File '{filename}': expected a dictionary of translations, but got {type(data).__name__}",
                    InvalidLocaleDocumentError,
                )

            self._root_tags[locale_code] = root.tag
            self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
            return {locale_code: data}

        except Et.ParseError as e:
            return self._throw(f"Error parsing XML file '{filename}': {e}", ParseError)
        except FileNotFoundError:
            return self._throw(f"Locale file '{filename}' not found during load.", FileNotFoundError)
        except Exception as e:
            return self._throw(f"Unknown error loading '{filename}': {e}", type(e))

    def save(self, filepath: Union[str, Path], data: Dict[str, Any]):
        """Save localization data to an XML file."""
        if not data:
            self._throw(f"Cannot save empty data to '{filepath}'", ValueError)

        filepath = Path(filepath)
        root_key = next(iter(data))
        root_content = data[root_key]
        root_tag = self._root_tags.get(root_key, "locale")
        root = Et.Element(root_tag)

        if isinstance(root_content, str):
            root.text = root_content
        elif isinstance(root_content, dict):
            self._dict_to_etree(root_content, root, root_key)

        tree = Et.ElementTree(root)
        if hasattr(Et, "indent"):
            Et.indent(tree)

        with open(filepath, "wb") as f:
            tree.write(f, encoding="utf-8", xml_declaration=True)

    def _etree_to_dict(self, node: Et.Element, locale_code: str = "", path: str = "") -> Union[Dict, List, str]:
        if node.attrib.get("list", "").lower() == "true":
            if locale_code and path:
                tag_dict = self._explicit_lists.setdefault(locale_code, {})
                tag_dict[path] = node[0].tag if len(node) > 0 else "item"

            return [self._etree_to_dict(child, locale_code, f"{path}.item") for child in node]

        has_children = len(node) > 0
        if not has_children or all(getattr(child, "tag", None) in self.INLINE_TAGS for child in node):
            return self._get_inner_xml(node)

        result: Dict[str, Any] = {}
        for child in node:
            if callable(child.tag):  # ElementTree uses callables for Comments
                result[f"comment_{id(child)}"] = self._etree_to_dict(child, locale_code, path)
                continue

            child_tag = str(child.tag)
            child_path = f"{path}.{child_tag}" if path else child_tag
            child_data = self._etree_to_dict(child, locale_code, child_path)

            if child_tag in result:
                existing = result[child_tag]
                if isinstance(existing, list):
                    existing.append(child_data)
                else:
                    result[child_tag] = [existing, child_data]
            else:
                result[child_tag] = child_data

        return result

    def _dict_to_etree(self, data: Dict[str, Any], parent: Et.Element, locale_code: str = "", path: str = "") -> None:
        for key, value in data.items():
            if key.startswith("comment_"):
                parent.append(Et.Comment(str(value)))
                continue

            current_path = f"{path}.{key}" if path else key
            item_tag = self._explicit_lists.get(locale_code, {}).get(current_path)
            is_explicit = item_tag is not None or (isinstance(value, list) and any(isinstance(i, list) for i in value))

            if isinstance(value, list) and not is_explicit:
                for item in value:
                    child = Et.SubElement(parent, key)
                    self._set_node_value(child, item, locale_code, current_path)
            else:
                attrib = {"list": "true"} if is_explicit else {}
                child = Et.SubElement(parent, key, attrib)
                self._set_node_value(child, value, locale_code, current_path)

    def _set_node_value(self, node: Et.Element, value: Any, locale_code: str, path: str) -> None:
        if isinstance(value, dict):
            self._dict_to_etree(value, node, locale_code, path)
            return

        if isinstance(value, list):
            item_tag = self._explicit_lists.get(locale_code, {}).get(path) or "item"
            for item in value:
                attrib = {"list": "true"} if isinstance(item, list) else {}
                item_node = Et.SubElement(node, item_tag, attrib)
                self._set_node_value(item_node, item, locale_code, f"{path}.item")
            return

        text_val = str(value)
        if "<" in text_val and ">" in text_val:
            try:
                fragment = Et.fromstring(f"<root>{text_val}</root>")
                node.text = fragment.text
                node.extend(list(fragment))
                return
            except Et.ParseError:
                pass

        node.text = text_val

    @staticmethod
    def _get_inner_xml(node: Et.Element) -> str:
        parts = [node.text or ""]

        for child in node:
            parts.append(Et.tostring(child, encoding="unicode"))

        return "".join(parts)

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> Union[Dict, NoReturn]:
        if self._strict:
            raise exc_type(msg)
        self._logger.log(lvl, msg)
        return {}
