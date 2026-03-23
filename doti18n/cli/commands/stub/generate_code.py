import logging
from dataclasses import dataclass
from textwrap import indent
from typing import Union

from doti18n.utils import _is_plural_dict

from .formatted_stub import generate_formatted_stub
from .icumf_stub import generate_icumf_stub
from .plural_stub import generate_plural_stub
from datetime import datetime, UTC


logger = logging.getLogger("doti18n.stub")
LIBRARY_CODE = """# Generated via doti18n at {time}
{extra_imports}
from typing import Any, overload, Optional, Union, Literal, List, Callable, Dict, Tuple, Iterator
from pathlib import Path


{stub_code}
class Node:
    pass


class BaseFormatter:
    def __init__(self, strict: bool): ...
    def __call__(self, t: "LocaleTranslator", node: Any, **kwargs) -> list[Union[None, Any]]: ...


class HTMLFormatter(BaseFormatter):
    def __init__(self, strict: bool): ...
    def __call__(self, t: "LocaleTranslator", node: Any, **kwargs) -> list[Union[None, Any]]: ...


class MarkdownFormatter(BaseFormatter):
    def __init__(self, strict: bool): ...
    def __call__(self, t: "LocaleTranslator", node: Any, **kwargs) -> list[Union[None, Any]]: ...


class ICUMF:
    def __init__(self, strict: bool = True, tag_formatter: type[BaseFormatter] = HTMLFormatter, 
    cache_size: int = 1024, **kwargs): ...
    def parse(self, string: str) -> Any: ...
    def compile(self, nodes: List[Node], formatter: Optional[BaseFormatter] = None) -> Callable: ...


class Loader:
    def __init__(self, strict: bool = False, icumf: Union[Optional[ICUMF], bool] = None): ...
    def get_supported_extensions(self) -> Tuple[str]: ...
    def load(self, filepath: Union[str, Path]) -> Union[Dict, List[Tuple[str, dict]]]: ...


class LocaleTranslator:
    def get(self, name: str) -> Any: ...

class LocaleData:
    def __init__(self, path: Union[str, Path], default_locale: str = "en", strict: bool = False, preload: bool = True, 
    loader: Optional[Loader] = None): ...
    def __contains__(self, locale_code: str) -> bool: ...
    @property
    def loaded_locales(self) -> List[str]: ...
    def get_locale(self, locale_code: str, default: Any = None) -> Union[Optional[LocaleTranslator], Any]: ..."""


@dataclass
class StubNamespace:
    name: str
    childs: dict
    args: dict


@dataclass
class StubLocale:
    name: str
    childs: dict
    args: dict


@dataclass
class StubList:
    name: str
    items: list


def fill_stub_namespace(locale_data: dict, element: StubNamespace):
    for key, value in locale_data.items():
        if isinstance(value, dict):
            if _is_plural_dict(value):
                element.args[key] = value
            else:
                element.childs[key] = fill_stub_namespace(value, StubNamespace(f"{element.name}_{key}", {}, {}))
        elif isinstance(value, list):
            items = []
            for n, v in enumerate(value):
                if isinstance(v, dict):
                    if _is_plural_dict(v):
                        items.append(v)
                    else:
                        child = fill_stub_namespace(v, StubNamespace(f"{element.name}_{key}_{n}", {}, {}))
                        items.append(child)
                else:
                    items.append(v)
            element.childs[key] = StubList(f"{element.name}_{key}", items)
        else:
            element.args[key] = value

    return element


def generate_stub_classes(locale_data: dict) -> list[StubLocale]:
    stub_classes = []
    for key, value in locale_data.items():
        locale = StubLocale(key, {}, {})
        for key_, value_ in value.items():
            if isinstance(value_, dict):
                if _is_plural_dict(value_):
                    locale.args[key_] = value_
                else:
                    locale.childs[key_] = fill_stub_namespace(value_, StubNamespace(f"{key}_{key_}", {}, {}))
            elif isinstance(value_, list):
                items = []
                for n, v in enumerate(value_):
                    if isinstance(v, dict):
                        if _is_plural_dict(v):
                            items.append(v)
                        else:
                            child = fill_stub_namespace(v, StubNamespace(f"{key}_{key_}_{n}", {}, {}))
                            items.append(child)
                    else:
                        items.append(v)
                locale.childs[key_] = StubList(f"{key}_{key_}", items)
            else:
                locale.args[key_] = value_

        stub_classes.append(locale)

    return stub_classes


def normalize_name(name: str) -> str:
    return "Namespace" + name.replace("_", " ").replace("-", " ").title().replace(" ", "").strip()


# ruff: noqa C901
def generate_class(cls: Union[StubLocale, StubNamespace, StubList], types: dict) -> str:
    """Generate stub class code for a given StubLocale or StubNamespace."""
    lines = []

    if isinstance(cls, StubNamespace):
        lines.append(f"class {normalize_name(cls.name)}(LocaleTranslator):")
    elif isinstance(cls, StubList):
        lines.append(f"class {normalize_name(cls.name)}(list):")
        item_types = []
        for i, item in enumerate(cls.items):
            if isinstance(item, dict) and _is_plural_dict(item):
                t = "Callable"
            elif isinstance(item, StubNamespace):
                t = normalize_name(item.name)
            elif isinstance(item, StubList):
                t = normalize_name(item.name)
            elif item is not None:
                t = type(item).__name__
            else:
                t = "Any"
            item_types.append(t)

            if t in ["str", "int", "float", "bool"]:
                lines.append(f"    _{i}: {t} = {repr(item)}")
            else:
                lines.append(f"    _{i}: {t} = ...")
            lines.append(f"    @overload")
            lines.append(f"    def __getitem__(self, index: Literal[{i}]) -> {t}: ...")

        unique_types = sorted(list(set(item_types)))
        if not unique_types:
            union_type = "Any"
        elif len(unique_types) == 1:
            union_type = unique_types[0]
        else:
            union_type = f"Union[{', '.join(unique_types)}]"

        lines.append(f"    def __iter__(self) -> Iterator[{union_type}]: ...")
        lines.append(f"    def __getitem__(self, index: Union[int, slice]) -> {union_type}: ...")
        return "\n".join(lines) + "\n\n"
    else:
        lines.append(f"class {cls.name.capitalize()}Locale(LocaleTranslator):")

    for key, value in cls.args.items():
        if value is None:
            lines.append(f"    {key} = None")
            continue

        if isinstance(value, str):
            sig, is_func = generate_icumf_stub(key, value)
            if is_func:
                lines.append(f"    {sig}")
            else:
                code, _ = generate_formatted_stub(key, value, types)
                lines.append(f"    {code}")

            continue

        if isinstance(value, dict):
            if _is_plural_dict(value):
                stub = generate_plural_stub(key, value)
                lines.append(indent(stub.rstrip(), "    "))
            else:
                lines.append(f"    {key}: dict = {repr(value)}")
            continue

        lines.append(f"    {key}: {type(value).__name__} = {repr(value)}")

    for key, value in cls.childs.items():
        name = normalize_name(value.name)
        lines.append(f"    {key}: {name}")

    return "\n".join(lines) + "\n\n"


STANDARD_TYPES = {
    "str",
    "int",
    "float",
    "bool",
    "list",
    "dict",
    "set",
    "tuple",
    "Any",
    "Union",
    "Callable",
    "Optional",
    "Literal",
    "List",
    "Dict",
    "Tuple",
    "Iterator",
}


# TODO: add support for types like Union[Type1, Type2]
def extra_imports(types: dict) -> str:
    imports = set()

    for path in types.values():
        if path in STANDARD_TYPES:
            continue

        if path.startswith("."):
            logger.error(f"Relative imports are not allowed: {path}. Skipping.")
            continue

        path_parts = path.split(".")
        if len(path_parts) > 1:
            module = ".".join(path_parts[:-1])
            class_name = path_parts[-1]
            imports.add(f"from {module} import {class_name}\n")
        else:
            imports.add(f"import {path}\n")

    return "".join(sorted(imports))


def generate_code(data: dict, default_locale: str = "en") -> str:
    """Generate stub code for locale data."""
    global LIBRARY_CODE
    code = []
    stub_classes = generate_stub_classes(data)
    if types := data[default_locale].get("__types__", None):
        imports = extra_imports(types)
        for key, value in types.items():
            types[key] = value.split(".")[-1]
    else:
        types = {}
        imports = ""

    for cls in stub_classes:

        def process_childs(stub_namespace: Union[StubNamespace, StubList]):
            nonlocal code
            if isinstance(stub_namespace, StubNamespace):
                for value in stub_namespace.childs.values():
                    process_childs(value)
            elif isinstance(stub_namespace, StubList):
                for item in stub_namespace.items:
                    if isinstance(item, (StubNamespace, StubList)):
                        process_childs(item)

            code.append(generate_class(stub_namespace, types))

        for child in cls.childs.values():
            process_childs(child)

        code.append(generate_class(cls, types))
        # class_name
        cn = f"{cls.name.capitalize()}Locale"
        LIBRARY_CODE += (
            f"\n    @overload"
            f"\n    def get_locale(self, locale_code: Literal['{cls.name}'], default: Any = None) -> {cn}: ..."
            f"\n    @overload"
            f"\n    def __getitem__(self, locale_code: Literal['{cls.name}']) -> {cn}: ..."
        )

    LIBRARY_CODE += (
        f"\n    @overload"
        f"\n    def __getitem__(self, locale_code: str) -> {default_locale.capitalize()}Locale: ...\n"
    )

    time = datetime.now(UTC).strftime("%Y.%m.%d %H:%M:%S UTC")
    return LIBRARY_CODE.format(stub_code="".join(code), time=time, extra_imports=imports)
