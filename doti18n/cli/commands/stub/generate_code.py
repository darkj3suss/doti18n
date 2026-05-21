import logging
from datetime import UTC, datetime

from .utils import StubLocale

logger = logging.getLogger("doti18n.stub")

LIBRARY_CODE_TEMPLATE = """# Generated via doti18n at {time}
{extra_imports}
from typing import Any, overload, Optional, Union, Literal, List, Callable, Dict, Tuple, Iterator, SupportsIndex
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
    @overload
    def get_locale(self, locale_code: str, default: Any = None) -> Union[Optional[LocaleTranslator], Any]: ...
{locale_overloads}"""


STANDARD_TYPES = frozenset(
    {
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
        "SupportsIndex",
    }
)


def build_extra_imports(types: dict) -> str:
    """Build import statements for extra types used in the stubs."""
    imports = set()
    for path in types.values():
        if path in STANDARD_TYPES:
            continue

        if path.startswith("."):
            logger.error(f"Relative imports are not allowed: {path}. Skipping.")
            continue

        path_parts = path.split(".")
        if len(path_parts) > 1:
            module, class_name = ".".join(path_parts[:-1]), path_parts[-1]
            imports.add(f"from {module} import {class_name}\n")
        else:
            imports.add(f"import {path}\n")

    return "".join(sorted(imports))


def generate_code(data: dict, default_locale: str = "en") -> str:
    """Generate Python stub code for the given locale data."""
    types = {}
    imports = ""
    default_data = data.get(default_locale, {})

    if "__types__" in default_data:
        types = default_data.pop("__types__")
        imports = build_extra_imports(types)
        types = {k: v.split(".")[-1] for k, v in types.items()}

    locales = [StubLocale(lang_code, locale_data) for lang_code, locale_data in data.items()]
    stub_code_blocks = []
    locale_overloads = []
    for locale in locales:
        stub_code_blocks.extend(locale.render_tree(types))
        locale_overloads.append(locale.generate_overloads())

    cn = None
    for stub_locale in locales:
        if stub_locale.name == default_locale:
            cn = stub_locale.class_name
            break

    locale_overloads.append(f"\n    @overload" f"\n    def __getitem__(self, locale_code: str) -> {cn}: ...\n")
    time_str = datetime.now(UTC).strftime("%Y.%m.%d %H:%M:%S UTC")

    return LIBRARY_CODE_TEMPLATE.format(
        stub_code="\n".join(stub_code_blocks),
        time=time_str,
        extra_imports=imports,
        locale_overloads="".join(locale_overloads),
    )
