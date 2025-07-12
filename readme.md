# doti18n [![PyPI version](https://badge.fury.io/py/doti18n.svg)](https://pypi.org/project/doti18n/) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/darkj3suss/doti18n/blob/main/LICENSE)

Simple and intuitive Python library for loading localizations from YAML files and accessing them easily using dot notation, with powerful support for plural forms and nested data structures.

## Description

doti18n provides a convenient way to manage your application's localization strings. By loading data from standard YAML files, the library allows you to access nested translations using a simple **dot syntax (`messages.status.online`) for dictionary keys** and **index syntax (`items[0]`) for list elements**. You can combine these for intuitive navigation through complex nested structures (`pages[0].title`).

Special attention is given to pluralization support using the [Babel](https://pypi.org/project/babel/) library, which is critical for correct localization across different languages. An automatic fallback mechanism to the default locale's value is also implemented if a key or path is missing in the requested locale.

The library offers both a forgiving non-strict mode (returning a special wrapper and logging warnings) and a strict mode (raising exceptions) for handling missing paths.

It's designed for ease of use and performance (data is loaded once during initialization and translator objects are cached).

## Features

*   Loading localization data from YAML files.
*   Intuitive access to nested data structures (dictionaries and lists) using **dot notation (`.`) for dictionary keys and index notation (`[]`) for list elements**.
*   Support for **combined access paths** (`data.list[0].nested_key`).
*   **Strict mode** (`strict=True`) to raise exceptions (`AttributeError`, `IndexError`, `TypeError`) on missing paths or incorrect usage.
*   **Non-strict mode** (default) to return a special `NoneWrapper` object and log a warning on missing paths.
*   Pluralization support for count-dependent strings (requires `Babel`).
*   Automatic fallback to the default locale if a key/path is missing in the current locale.
*   Caching of loaded data and translator objects for efficient access.
*   Handles explicit `null` values in YAML, distinguishing them from missing paths.

## Installation

doti18n is available on [PyPI](https://pypi.org/project/doti18n/).

Install the basic version (without pluralization support):

```bash
pip install doti18n
```

For pluralization support (recommended), install with the optional `pluralization` dependency:

```bash
pip install doti18n[pluralization]
```

**Note:** Pluralization support is implemented using the [Babel](https://pypi.org/project/babel/) library. If you install doti18n without the `[pluralization]` optional dependency, pluralization functionality will be limited or unavailable, and the library will log a warning about the missing Babel dependency.

## Project Status

This project is in an early stage of development (**Alpha**). The API may change in future versions before reaching a stable (1.0.0) release. Any feedback and suggestions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/darkj3suss/doti18n/blob/main/LICENSE) file for details.

## Contact

If you have questions, feel free to open an issue on GitHub.
Or you can message me on [Telegram](https://t.me/darkjesuss)