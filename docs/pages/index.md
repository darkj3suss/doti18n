<div style="display: flex; justify-content: center;">
    <img src="https://i.ibb.co/0RWMD4HM/logo.png" alt="doti18n">
</div>
<div style="display: flex; justify-content: center;">
    <a href="https://pypi.org/project/doti18n/"><img src="https://badge.fury.io/py/doti18n.svg" alt="PyPI Version"></a> <a href="https://github.com/darkj3suss/doti18n/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
</div>

**doti18n** is a Python library that allows you to access localization data (YAML, JSON, XML) using dot-notation instead of dictionary lookups. 

It focuses on type safety by generating `.pyi` stubs, allowing IDEs to provide autocompletion and enabling linters to catch missing keys or other errors.

---

## Comparison

The main goal of doti18n is to replace string-based lookups with object navigation.

```python
# Traditional dictionary lookup
locales['en']['messages']['errors']['connection']

# gettext style
_("messages.errors.connection")

# doti18n style
i18n["en"].messages.errors.connection
```

## Features

### Type Safety & Autocompletion
doti18n includes a CLI tool that scans your locale files and generates **[PEP 561](https://peps.python.org/pep-0561)** compatible type stubs.

- **IDE Autocompletion:** Editors like VS Code and PyCharm will suggest available keys as you type.
- **Validation:** Static analysis tools (mypy, pyright) will flag errors if you reference a key that doesn't exist in your translation files.

### Pluralization
The library uses [Babel](https://babel.pocoo.org/) for pluralization, ensuring correct rules for different languages. It supports:

- Standard CLDR plural forms (zero, one, two, few, many, other).
- Variable interpolation.
- Nested structures.

### Execution Modes
You can configure how the library handles missing keys:

- **Strict Mode:** Raises exceptions for invalid paths. Recommended for testing and CI/CD.
- **Non-Strict Mode:** Returns a safe wrapper object and logs a warning instead of crashing. Recommended for production.

## Project Status

!!! warning "Alpha Release"
    This project is in the **Alpha** stage. The internal API and method signatures may undergo changes before the 1.0.0 release.

## Next Steps
- **[Getting started](getting_started.md)**: Installation and initial setup.
- **[Usage](usage/supported_formats.md)**: Supported formats (YAML, JSON, XML), pluralization examples, and interpolation(formatting).
- **[CLI](cli/stub.md)**: How to generate type definitions for your project.