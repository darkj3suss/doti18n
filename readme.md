[![PyPI version](https://badge.fury.io/py/doti18n.svg)](https://pypi.org/project/doti18n/) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/darkj3suss/doti18n/blob/main/LICENSE)

<div align="display: flex; justify-content: center;">
  <img src="https://i.ibb.co/0RWMD4HM/logo.png" alt="doti18n" width="90%"/>
  <br>
  <b>Type-safe localization library for Python.</b>
  <br>
  Access YAML, JSON, and XML translations using dot-notation.
</div>

---

## Overview

**doti18n** allows you to replace string-based dictionary lookups with intuitive object navigation. Instead of `locales['en']['messages']['error']`, just write `locales["en"]messages.error`.

It focuses on **Developer Experience (DX)** by providing a CLI tool to generate `.pyi` stubs. This enables **IDE autocompletion** and allows static type checkers (mypy, pyright) to catch missing keys at build time.

### Key Features

*   **Dot-Notation:** Access nested keys via attributes (`data.key`) and lists via indices (`items[0]`).
*   **Type Safety:** Generate stubs to get full IDE support and catch typos instantly.
*   **Pluralization:** robust support powered by [Babel](https://babel.pocoo.org/).
*   **Format Agnostic:** Supports YAML, JSON, and XML out of the box.
*   **Safety Modes:** 
    *   **Strict:** Raises exceptions for missing keys (good for dev/test).
    *   **Non-strict:** Returns a safe wrapper and logs warnings (good for production).
*   **Fallback:** Automatically falls back to the default locale if a key is missing.

## Installation

```bash
pip install doti18n
```

If you use YAML files:
```bash
pip install doti18n[yaml]
```

## Usage

**1. Create a localization file** (`locales/en.yaml`):

```yaml
greeting: "Hello {}!"
farewell: "Goodbye $name!"
items:
    - name: "Item 1"
    - name: "Item 2"
notifications:
    one: "You have {count} new notification."
    other: "You have {count} new notifications."
```

**2. Access it in Python:**

```python
from doti18n import LocaleData

# Initialize (loads and caches data)
i18n = LocaleData("locales")
en = i18n["en"]

# 1. Standard formatting (Python-style)
print(en.greeting("John"))           # Output: Hello John!

# 2. Variable formatting (Shell-style)
print(en.farewell(name="Alice"))     # Output: Goodbye Alice!

# 3. Raw strings and graceful handling
print(en.farewell)                   # Output: Goodbye $name! (Raw string)
print(en.farewell())                 # Output: Goodbye ! (Missing var handled)

# 4. List access
print(en.items[0].name)              # Output: Item 1

# 5. Pluralization
print(en.notifications(1))           # Output: You have 1 new notification.
print(en.notifications(5))           # Output: You have 5 new notifications.
```

## CLI & Type Safety

doti18n comes with a CLI to generate type stubs (`.pyi`).

**Why use it?**
1.  **Autocompletion:** Your IDE will suggest available keys as you type.
2.  **Validation:** Static analysis tools will flag errors if you try to access a key that doesn't exist.

**Commands:**

```bash
# Generate stubs for all files in 'locales/' (default lang: en)
python -m doti18n stub locales/

# Generate stubs with a specific default language
python -m doti18n stub locales/ -lang fr

# Clean up generated stubs
python -m doti18n stub --clean
```

> **Note:** Run this inside your virtual environment to ensure stubs are generated for the installed package.

## Project Status

**Alpha Stage:** The API is stable but may evolve before the 1.0.0 release. Feedback and feature requests are highly appreciated!

## License

MIT License. See [LICENSE](https://github.com/darkj3suss/doti18n/blob/main/LICENSE) for details.

## Contact

*   **Issues:** [GitHub Issues](https://github.com/darkj3suss/doti18n/issues)
*   **Direct:** [Telegram](https://t.me/darkjesuss)