from abc import ABC, abstractmethod
from textwrap import indent
from typing import Any, Union

from doti18n.utils import _is_plural_dict

from .formatted_stub import generate_formatted_stub, generate_plural_stub
from .icumf_stub import generate_icumf_stub
from .normalize_name import normalize_name


class StubBase(ABC):
    """Abstract base class for all stub nodes (namespaces and lists)."""

    def __init__(self, name: str):
        """Initialize a StubNode."""
        self.name = name

    @abstractmethod
    def render(self, types: dict) -> str:
        """Render the stub as a code block."""
        pass

    @abstractmethod
    def render_tree(self, types: dict) -> list[str]:
        """Render the stub and all nested stubs as code blocks."""
        pass

    @property
    @abstractmethod
    def class_name(self) -> str:
        """Generate a valid Python class name for the stub based on its name."""
        pass


class StubList(StubBase):
    """Represent a list in the locale data."""

    def __init__(self, name: str, items: list):
        """Initialize a StubList."""
        super().__init__(name)
        self.items: list[Union[Any, StubBase]] = []
        self._parse_items(items)

    def _parse_items(self, items: list):
        for n, v in enumerate(items):
            if isinstance(v, dict):
                if _is_plural_dict(v):
                    self.items.append(v)
                else:
                    self.items.append(StubNamespace(f"{self.name}_{n}", v))
            elif isinstance(v, list):
                self.items.append(StubList(f"{self.name}_{n}", v))
            else:
                self.items.append(v)

    @property
    def class_name(self) -> str:
        """Generate a class name for the list stub based on its name, ensuring it is a valid Python identifier."""
        return normalize_name(self.name)

    def render_tree(self, types: dict) -> list[str]:
        """Render the list stub and all nested stubs as code blocks."""
        code_blocks = []
        for item in self.items:
            if isinstance(item, StubBase):
                code_blocks.extend(item.render_tree(types))
        code_blocks.append(self.render(types))
        return code_blocks

    def render(self, types: dict) -> str:
        """Render the list stub as a class with overloads for each item."""
        lines = [f"class {self.class_name}(list):"]
        item_types = set()

        if not self.items:
            lines.append("    pass\n")
            return "\n".join(lines)

        for i, item in enumerate(self.items):
            if isinstance(item, dict) and _is_plural_dict(item):
                t = "Callable"
            elif isinstance(item, StubBase):
                t = item.class_name
            elif item is not None:
                t = type(item).__name__
            else:
                t = "Any"

            item_types.add(t)

            if t in ("str", "int", "float", "bool"):
                lines.append(f"    _{i}: {t} = {repr(item)}")
            else:
                lines.append(f"    _{i}: {t} = ...")
            lines.append("    @overload")
            lines.append(f"    def __getitem__(self, index: Literal[{i}]) -> {t}: ...")

        unique_types = sorted(item_types)
        union_type = (
            unique_types[0]
            if len(unique_types) == 1
            else f"Union[{', '.join(unique_types)}]" if unique_types else "Any"
        )

        lines.append(f"    def __iter__(self) -> Iterator[{union_type}]: ...")
        lines.append(f"    def __getitem__(self, index: Union[SupportsIndex, slice]) -> {union_type}: ...")

        return "\n".join(lines) + "\n"


class StubNamespace(StubBase):
    """Represent a namespace in the locale data."""

    def __init__(self, name: str, data: dict | list):
        """Initialize a StubNamespace."""
        super().__init__(name)
        self.args: dict[str, Any] = {}
        self.childs: dict[str, StubBase] = {}
        if isinstance(data, list):
            for item in data:
                self._parse_data(item)
        else:
            self._parse_data(data)

    def _parse_data(self, data: dict):
        for key, value in data.items():
            if isinstance(value, dict):
                if _is_plural_dict(value):
                    self.args[key] = value
                else:
                    self.childs[key] = StubNamespace(f"{self.name}_{key}", value)
            elif isinstance(value, list):
                self.childs[key] = StubList(f"{self.name}_{key}", value)
            else:
                self.args[key] = value

    @property
    def class_name(self) -> str:
        """Generate a class name for the namespace stub based on its name, ensuring it is a valid Python identifier."""
        return normalize_name(self.name)

    @property
    def base_class(self) -> str:
        """Determine the base class for the namespace stub."""
        return "LocaleTranslator"

    def render_tree(self, types: dict) -> list[str]:
        """Render the namespace stub and all nested stubs as code blocks."""
        code_blocks = []
        for child in self.childs.values():
            code_blocks.extend(child.render_tree(types))

        code_blocks.append(self.render(types))
        return code_blocks

    def render(self, types: dict) -> str:
        """Render the namespace stub as a class with attributes for each key and overloads for ICUMF strings."""
        lines = [f"class {self.class_name}({self.base_class}):"]
        if not self.args and not self.childs:
            lines.append("    pass\n")
            return "\n".join(lines)

        if local_types := self.args.get("__types__", {}):
            types |= local_types

        for key, value in self.args.items():
            if value is None:
                lines.append(f"    {key} = None")
            elif isinstance(value, str):
                sig, is_func = generate_icumf_stub(key, value, types)
                if is_func:
                    lines.append(f"    {sig}")
                else:
                    code, _ = generate_formatted_stub(key, value, types)
                    lines.append(f"    {code}")
            elif isinstance(value, dict) and _is_plural_dict(value):
                stub = generate_plural_stub(key, value, types)
                lines.append(indent(stub.rstrip(), "    "))
            else:
                lines.append(f"    {key}: {type(value).__name__} = {repr(value)}")

        for key, child in self.childs.items():
            lines.append(f"    {key}: {child.class_name}")

        return "\n".join(lines) + "\n"


class StubLocale(StubNamespace):
    """Represent a locale in the locale data."""

    @property
    def class_name(self) -> str:
        """Generate a class name for the locale stub based on its name."""
        return f"{self.name.capitalize()}Locale"

    def generate_overloads(self) -> str:
        """Generate overloads for the get_locale and __getitem__ methods for this locale."""
        cn = self.class_name
        return (
            f"\n    @overload"
            f"\n    def get_locale(self, locale_code: Literal['{self.name}'], default: Any = None) -> {cn}: ..."
            f"\n    @overload"
            f"\n    def __getitem__(self, locale_code: Literal['{self.name}']) -> {cn}: ..."
        )
