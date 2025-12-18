import os
from dataclasses import dataclass

from doti18n.loaders import Loader
from doti18n.utils import _deep_merge
from .formatted_string_stub import generate_stub_signature


LIBRARY_CODE = \
    """
class LocaleTranslator:
    def __getattr__(self, name: str) -> Any: ...


class LocaleData:
    def __init__(self, locales_dir: str, default_locale: str = "en", strict: bool = False, preload: bool = True): ...
    def __contains__(self, locale_code: str) -> bool: ...
    @property
    def loaded_locales(self) -> List[str]: ...
    def get_translation(self, locale_code: str, default: Any = None) -> Union[Optional[LocaleTranslator], Any]: ..."""


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


def fill_stub_namespace(locale_data: dict, element: StubNamespace):
    for key, value in locale_data.items():
        if isinstance(value, dict):
            element.childs[key] = fill_stub_namespace(value, StubNamespace(f"{element.name}_{key}", {}, {}))
        elif isinstance(value, list):
            element.args[key] = []
            for n, v in enumerate(value):
                if isinstance(v, dict):
                    element.args[key].append(fill_stub_namespace(v, StubNamespace(f"{element.name}_{key}_{n}", {}, {})))
                else:
                    element.args[key].append(v)
        else:
            element.args[key] = value

    return element


def generate_stub_classes(locale_data: dict) -> list[StubLocale]:
    stub_classes = []
    for key, value in locale_data.items():
        locale = StubLocale(key, {}, {})
        for key_, value_ in value.items():
            if isinstance(value_, dict):
                locale.childs[key_] = fill_stub_namespace(value_, StubNamespace(key_, {}, {}))
            else:
                locale.args[key_] = value_

        stub_classes.append(locale)

    return stub_classes


def normalize_name(name: str) -> str:
    return "Namespace" + name.replace("_", " ").replace("-", " ").title().replace(" ", "").strip()


def generate_class(cls: StubLocale | StubNamespace):
    lines = []

    if isinstance(cls, StubNamespace):
        lines.append(f"class {normalize_name(cls.name)}:")
    else:
        lines.append(f"class {cls.name.capitalize()}Locale:")

    for key, value in cls.args.items():
        _type = None if value is None else type(value).__name__
        if _type == "list":
            line = f"    {key}: list = ["
            for n, v in enumerate(value):
                if isinstance(v, StubNamespace):
                    line += f"{normalize_name(v.name)}(), "
                elif isinstance(v, str):
                    data, flag = generate_stub_signature(f"{key}_{n}", v)
                    if flag:
                        lines.append(f"    {data}")
                        line += f"self.{key}_{n}, "
                    else:
                        line += f"{repr(v)}, "
                else:
                    line += f"{repr(v)}, "
            lines.append(line[:-2] + "]")

        elif _type == "str":
            data, flag = generate_stub_signature(key, value)
            if flag:
                lines.append(f"    {data}")
            else:
                lines.append(f"    {key}: {_type} = {repr(value)}")

        else:
            lines.append(f"    {key}: {_type} = {repr(value)}")

    for key, value in cls.childs.items():
        name = normalize_name(value.name)
        lines.append(f"    {key}: {name} = {name}()")

    return "\n".join(lines) + "\n\n"


def generate_code(data: dict, default_locale: str = "en") -> str:
    global LIBRARY_CODE
    code = []
    stub_classes = generate_stub_classes(data)
    for cls in stub_classes:
        def process_childs(stub_namespace: StubNamespace):
            nonlocal code
            for value in stub_namespace.childs.values():
                process_childs(value)

            for value in stub_namespace.args.values():
                if isinstance(value, list):
                    for v in value:
                        if isinstance(v, StubNamespace):
                            process_childs(v)

            code.append(generate_class(stub_namespace))

        for child in cls.childs.values():
            process_childs(child)

        code.append(generate_class(cls))
        LIBRARY_CODE += f"\n    @overload\n    def __getitem__(self, locale_code: Literal['{cls.name}']) -> {cls.name.capitalize()}Locale: ..."

    LIBRARY_CODE += f"\n    @overload\n    def __getitem__(self, locale_code: str) -> {default_locale.capitalize()}Locale: ...\n"
    return "from typing import Any, overload, Optional, Union, Literal, List\n\n" + "".join(code) + LIBRARY_CODE
