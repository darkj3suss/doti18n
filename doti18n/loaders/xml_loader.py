import logging
import xml.etree.ElementTree as Et
from pathlib import Path
from typing import Any, NoReturn

from ..errors import (
    EmptyFileError,
    InvalidLocaleDocumentError,
    ParseError,
)
from ..utils import _get_locale_code
from .base_loader import BaseLoader


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
        self._root_tags: dict[str, str] = {}
        self._explicit_lists: dict[str, dict[str, str]] = {}

    def load(self, filepath: str | Path) -> dict[str, Any]:
        """Load and processes localization data from an XML file."""
        filepath = Path(filepath)
        filename = filepath.name

        try:
            tree = Et.parse(filepath)
            root = tree.getroot()
            locale_code = _get_locale_code(filename)
            data = self._etree_to_dict(root, locale_code)

        except Et.ParseError as e:
            return self._throw(f"Error parsing XML file '{filename}': {e}", ParseError)
        except FileNotFoundError:
            return self._throw(f"Locale file '{filename}' not found during load.", FileNotFoundError)
        except Exception as e:
            return self._throw(f"Unknown error loading '{filename}': {e}", type(e))

        if not data:
            return self._throw(f"Locale file '{filename}' is empty", EmptyFileError)

        if not isinstance(data, dict):
            return self._throw(
                f"File '{filename}': expected a dictionary of translations, but got {type(data).__name__}",
                InvalidLocaleDocumentError,
            )

        self._root_tags[locale_code] = root.tag
        self._logger.info(f"Loaded locale data for: '{locale_code}' from '{filename}'")
        return {locale_code: data}

    def _etree_to_dict(self, node: Et.Element, locale_code: str = "", path: str = "") -> dict | list | str:
        if node.attrib.get("list", "").lower() == "true":
            if locale_code and path:
                tag_dict = self._explicit_lists.setdefault(locale_code, {})
                tag_dict[path] = node[0].tag if len(node) > 0 else "item"

            return [self._etree_to_dict(child, locale_code, f"{path}.item") for child in node]

        has_children = len(node) > 0
        if not has_children or all(getattr(child, "tag", None) in self.INLINE_TAGS for child in node):
            return self._get_inner_xml(node)

        result: dict[str, Any] = {}
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

    @staticmethod
    def _get_inner_xml(node: Et.Element) -> str:
        parts = [node.text or ""]

        for child in node:
            parts.append(Et.tostring(child, encoding="unicode"))

        return "".join(parts)

    def _throw(self, msg: str, exc_type: type, lvl: int = logging.ERROR) -> dict | NoReturn:
        if self._strict:
            raise exc_type(msg)
        else:
            self._logger.log(lvl, msg)
            return {}
