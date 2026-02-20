from dataclasses import dataclass
from textwrap import indent
from typing import Union

from doti18n.utils import _is_plural_dict

from .formatted_stub import generate_formatted_stub
from .icumf_stub import generate_icumf_stub
from .plural_stub import generate_plural_stub
from datetime import datetime, UTC

LIBRARY_CODE = """# Generated via doti18n at {time}
from typing import Any, overload, Optional, Union, Literal, List, Callable, Dict, Tuple
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
    def __init__(self, strict: bool = True, tag_formatter: type[BaseFormatter] = HTMLFormatter, cache_size: int = 1024, **kwargs): ...
    def parse(self, string: str) -> Any: ...
    def compile(self, nodes: List[Node], formatter: Optional[BaseFormatter] = None) -> Callable: ...


class Loader:
    def __init__(self, strict: bool = False, icumf: Union[Optional[ICUMF], bool] = None): ...
    def get_supported_extensions(self) -> Tuple[str]: ...
    def load(self, filepath: Union[str, Path]) -> Union[Dict, List[Tuple[str, dict]]]: ...


class LocaleTranslator:
    def get(self, name: str) -> Any: ...
    def __getattr__(self, name: str) -> Any: ...

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
    list_childs: dict = None

    def __post_init__(self):
        if self.list_childs is None:
            self.list_childs = {}


@dataclass
class StubLocale:
    name: str
    childs: dict
    args: dict
    list_childs: dict = None

    def __post_init__(self):
        if self.list_childs is None:
            self.list_childs = {}


def fill_stub_namespace(locale_data: dict, element: StubNamespace):
    for key, value in locale_data.items():
        if isinstance(value, dict):
            if _is_plural_dict(value):
                element.args[key] = value
            else:
                element.childs[key] = fill_stub_namespace(value, StubNamespace(f"{element.name}_{key}", {}, {}))
        elif isinstance(value, list):
            element.args[key] = []
            element.list_childs[key] = []
            for n, v in enumerate(value):
                if isinstance(v, dict):
                    if _is_plural_dict(v):
                        element.args[key].append(v)
                        element.list_childs[key].append(None)
                    else:
                        child = fill_stub_namespace(v, StubNamespace(f"{element.name}_{key}_{n}", {}, {}))
                        element.args[key].append(None)
                        element.list_childs[key].append(child)
                else:
                    element.args[key].append(v)
                    element.list_childs[key].append(None)
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
                locale.args[key_] = []
                locale.list_childs[key_] = []
                for n, v in enumerate(value_):
                    if isinstance(v, dict):
                        if _is_plural_dict(v):
                            locale.args[key_].append(v)
                            locale.list_childs[key_].append(None)
                        else:
                            child = fill_stub_namespace(v, StubNamespace(f"{key}_{key_}_{n}", {}, {}))
                            locale.args[key_].append(None)
                            locale.list_childs[key_].append(child)
                    else:
                        locale.args[key_].append(v)
                        locale.list_childs[key_].append(None)
            else:
                locale.args[key_] = value_

        stub_classes.append(locale)

    return stub_classes


def normalize_name(name: str) -> str:
    return "Namespace" + name.replace("_", " ").replace("-", " ").title().replace(" ", "").strip()


# ruff: noqa C901
def generate_class(cls: Union[StubLocale, StubNamespace]):
    """Generate stub class code for a given StubLocale or StubNamespace."""
    lines = []

    if isinstance(cls, StubNamespace):
        lines.append(f"class {normalize_name(cls.name)}:")
    else:
        lines.append(f"class {cls.name.capitalize()}Locale(LocaleTranslator):")

    for key, value in cls.args.items():
        if value is None:
            lines.append(f"    {key}: None = None")
            continue

        if isinstance(value, str):
            sig, is_func = generate_icumf_stub(key, value)
            if is_func:
                lines.append(f"    {sig}")
            else:
                code, _ = generate_formatted_stub(key, value)
                lines.append(f"    {code}")

            continue

        if isinstance(value, dict):
            if _is_plural_dict(value):
                stub = generate_plural_stub(key, value)
                lines.append(indent(stub.rstrip(), "    "))
            else:
                lines.append(f"    {key}: dict = {repr(value)}")
            continue

        if isinstance(value, list):
            types = []
            for i, item in enumerate(value):
                if isinstance(item, dict) and _is_plural_dict(item):
                    stub_name = f"{key}_{i}"
                    stub = generate_plural_stub(stub_name, item)
                    lines.append(indent(stub.rstrip(), "    "))
                    types.append(f"Callable")
                elif key in cls.list_childs and i < len(cls.list_childs[key]) and cls.list_childs[key][i]:
                    types.append(normalize_name(cls.list_childs[key][i].name))
                elif item is not None:
                    types.append(type(item).__name__)
                else:
                    types.append("Any")

            unique_types = []
            for t in types:
                if t not in unique_types:
                    unique_types.append(t)

            if len(unique_types) == 1:
                type_hint = f"List[{unique_types[0]}]"
            elif len(unique_types) > 1:
                type_hint = f"List[Union[{', '.join(unique_types)}]]"
            else:
                type_hint = "List[Any]"

            lines.append(f"    {key}: {type_hint}")
            continue

        lines.append(f"    {key}: {type(value).__name__} = {repr(value)}")

    for key, value in cls.childs.items():
        name = normalize_name(value.name)
        lines.append(f"    {key}: {name}")

    return "\n".join(lines) + "\n\n"


def generate_code(data: dict, default_locale: str = "en") -> str:
    """Generate stub code for locale data."""
    global LIBRARY_CODE
    code = []
    stub_classes = generate_stub_classes(data)
    for cls in stub_classes:

        def process_childs(stub_namespace: StubNamespace):
            nonlocal code
            for value in stub_namespace.childs.values():
                process_childs(value)

            for key, v in stub_namespace.list_childs.items():
                for item in v:
                    if item:
                        process_childs(item)

            code.append(generate_class(stub_namespace))

        for child in cls.childs.values():
            process_childs(child)

        for v in cls.list_childs.values():
            for item in v:
                if item:
                    process_childs(item)

        code.append(generate_class(cls))
        LIBRARY_CODE += (
            f"\n    @overload"
            f"\n    def __getitem__(self, locale_code: Literal['{cls.name}']) -> {cls.name.capitalize()}Locale: ..."
        )

    LIBRARY_CODE += (
        f"\n    @overload"
        f"\n    def __getitem__(self, locale_code: str) -> {default_locale.capitalize()}Locale: ...\n"
    )

    time = datetime.now(UTC).strftime("%Y.%m.%d %H:%M:%S UTC")
    return LIBRARY_CODE.format(stub_code="".join(code), time=time)
