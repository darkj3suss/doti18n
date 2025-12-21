[![PyPI version](https://badge.fury.io/py/doti18n.svg)](https://pypi.org/project/doti18n/) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/darkj3suss/doti18n/blob/main/LICENSE)
<div style="align:center">
<img src="https://i.ibb.co/0RWMD4HM/logo.png" alt="doti18n">
</div>

Simple and intuitive Python library for loading localizations from YAML, JSON, XML files and accessing them easily using dot notation, with powerful support for plural forms and nested data structures.
It also gives you strong DX(Developer Experience) with stubs generation for your localization files.

## Description

doti18n provides a convenient way to manage your application's localization strings. By loading data from files, the library allows you to access nested translations using a simple **dot syntax (`messages.status.online`) for dictionary keys** and **index syntax (`items[0]`) for list elements**. You can combine these for intuitive navigation through complex nested structures (`pages[0].title`).

Special attention is given to pluralization support using the [Babel](https://pypi.org/project/babel/) library, which is critical for correct localization across different languages. An automatic fallback mechanism to the default locale's value is also implemented if a key or path is missing in the requested locale.

The library offers both a forgiving non-strict mode (returning a special wrapper and logging warnings) and a strict mode (raising exceptions) for handling missing paths.

It's designed for ease of use and performance (data is loaded once during initialization and translator objects are cached).

## Features

*   Loading localization data from YAML, JSON, XML files.
*   Intuitive access to nested data structures (dictionaries and lists) using **dot notation (`.`) for dictionary keys and index notation (`[]`) for list elements**.
*   Support for **combined access paths** (`data.list[0].nested_key`).
*   CLI tool for generating type stubs for your localization files to enhance IDE autocompletion and type-checking.
*   **Strict mode** (`strict=True`) to raise exceptions on missing paths or incorrect usage.
*   **Non-strict mode** (default) to return a special `NoneWrapper` object and log a warning on missing paths or incorrect usage.
*   Pluralization support for count-dependent strings (requires `Babel`).
*   Automatic fallback to the default locale if a key/path is missing in the current locale.
*   Caching of loaded data and translator objects for efficient access.

## Installation

doti18n is available on [PyPI](https://pypi.org/project/doti18n/).

Instaling:

```bash
pip install doti18n
```

## Usage
Here's a basic example of how to use doti18n:

Let's say you have a YAML file like this:
```yaml
# locales/en.yaml
greeting: "Hello {}!"
farewell: "Goodbye $name!"
items:
    - name: "Item 1"
    - name: "Item 2"
notifications:
    one: "You have {count} new notification."
    other: "You have {count} new notifications."
```

You can load and use it as follows:

```python
# Import main class
from doti18n import LocaleData

# Create a LocaleData instance
i18n = LocaleData("locales")

# Access translations
print(i18n["en"].greeting("John"))  # Output: Hello John!
print(i18n["en"].farewell(name="Alice"))  # Output: Goodbye Alice!
print(i18n["en"].farewell)  # Output: Goodbye $name!
print(i18n["en"].farewell())  # Output: Goodbye !
print(i18n["en"].items[0].name)  # Output: Item 1
print(i18n["en"].notifications(1))  # Output: You have 1 new notification.
print(i18n["en"].notifications(5))  # Output: You have 5 new notifications.

# You also can get LocaleTranslator object directly
t = i18n["en"]
print(t.notifications(2))  # Output: You have 2 new notifications.

# Even more, you can do this for any level of nesting
it = t.items
print(it[1].name)  # Output: Item 2
```

### CLI

Stub generator is available via the CLI command `doti18n stub` - helper that creates type stubs for your translations.

What it does and why you want it:
* Scans all locale files in the provided directory and collects the keys structure.
* Generates `doti18n/__init__.pyi` with classes and method signatures for each locale (namespaces, keys and formatted-string signatures).
* Provides IDE autocompletion and helps type-checkers (mypy, Pyright) catch typos in translation keys - makes working with localizations safer and more convenient.

Usage examples:

```
python -m doti18n stub locales/              # generate stubs (default locale = en)
python -m doti18n stub locales/ -lang fr     # set another default locale
python -m doti18n stub --clean               # remove previously generated stubs
```

Note: the command will warn if run outside a virtual environment - it's recommended to run it inside a venv to avoid dependency conflicts.

## Project Status

This project is in an early stage of development (**Alpha**). The API may change in future versions before reaching a stable (1.0.0) release. Any feedback and suggestions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/darkj3suss/doti18n/blob/main/LICENSE) file for details.

## Contact

If you have questions, feel free to open an issue on GitHub.
Or you can message me on [Telegram](https://t.me/darkjesuss)