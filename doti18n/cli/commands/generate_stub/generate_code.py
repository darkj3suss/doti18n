from dataclasses import dataclass
from .formatted_string_stub import generate_stub_signature
from .plural_stub import generate_plural_stub
from doti18n.utils import _is_plural_dict
from textwrap import indent


LIBRARY_CODE = \
    """
class LocaleTranslator:
    def get(self, name: str) -> Any: ...


class LocaleData:
    def __init__(self, locales_dir: str, default_locale: str = "en", strict: bool = False, preload: bool = True): ...
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


def fill_stub_namespace(locale_data: dict, element: StubNamespace):
    for key, value in locale_data.items():
        if isinstance(value, dict):
            if _is_plural_dict(value):
                element.args[key] = value
            else:
                element.childs[key] = fill_stub_namespace(value, StubNamespace(f"{element.name}_{key}", {}, {}))
        elif isinstance(value, list):
            element.args[key] = []
            for n, v in enumerate(value):
                if isinstance(v, dict):
                    if _is_plural_dict(v):
                        element.args[key].append(v)
                    else:
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
                if _is_plural_dict(value_):
                    locale.args[key_] = value_
                else:
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
        lines.append(f"class {cls.name.capitalize()}Locale(LocaleTranslator):")

    for key, value in cls.args.items():
        if value is None:
            lines.append(f"    {key}: None = None")
            continue

        if isinstance(value, str):
            sig, is_func = generate_stub_signature(key, value)
            if is_func:
                lines.append(f"    {sig}")
            else:
                lines.append(f"    {key}: str = {repr(value)}")
            continue

        if isinstance(value, dict):
            if _is_plural_dict(value):
                stub = generate_plural_stub(key, value)
                lines.append(indent(stub.rstrip(), '    '))
            else:
                lines.append(f"    {key}: dict = {repr(value)}")
            continue

        if isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict) and _is_plural_dict(item):
                    stub_name = f"{key}_{i}"
                    stub = generate_plural_stub(stub_name, item)
                    lines.append(indent(stub.rstrip(), '    '))
            lines.append(f"    {key}: list = {repr(value)}")
            continue

        lines.append(f"    {key}: {type(value).__name__} = {repr(value)}")

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

            for v in stub_namespace.args.values():
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict) and _is_plural_dict(item):
                            pass

            code.append(generate_class(stub_namespace))

        for child in cls.childs.values():
            process_childs(child)

        code.append(generate_class(cls))
        LIBRARY_CODE += f"\n    @overload\n    def __getitem__(self, locale_code: Literal['{cls.name}']) -> {cls.name.capitalize()}Locale: ..."

    LIBRARY_CODE += f"\n    @overload\n    def __getitem__(self, locale_code: str) -> {default_locale.capitalize()}Locale: ...\n"
    header = "from typing import Any, overload, Optional, Union, Literal, List\n\n"
    return header + "".join(code) + LIBRARY_CODE
