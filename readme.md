[![PyPI version](https://badge.fury.io/py/doti18n.svg)](https://pypi.org/project/doti18n/) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/darkj3suss/doti18n/blob/main/LICENSE)

<div align="center">
  <img src="https://i.ibb.co/0RWMD4HM/logo.png" alt="doti18n" width="90%"/>
  <br>
  <b>Modern, type-safe i18n / l10n library for Python.</b>
  <br>
  The alternative to standart i18n libraries with dot-notation, ICU Message Format, IDE autocompletion and powerful CLI.
</div>

---

## Overview

**doti18n** allows you to replace string-based dictionary lookups with intuitive object navigation. Instead of `i18n["en"]["messages"]["error"]`, just write `i18n["en"].messages.error`.

It focuses on **Developer Experience (DX)** by providing a CLI tool to generate `.pyi` stubs. This enables **IDE autocompletion** and allows static type checkers (mypy, pyright) to catch missing keys, typo and type mismatching at build time.

### Key Features

*   **Dot-Notation:** Access nested keys via attributes (`data.key`) and lists via indices (`items[0]`).
*   **Type Safety:** Generate stubs to get full IDE support and catch typos instantly.
*   **Advanced ICUMF:** Full support for **ICU Message Format** including nested `select`, `plural`, and custom formatters.
*   **Pluralization:** Robust support powered by [Babel](https://babel.pocoo.org/).
*   **Format Agnostic:** Supports YAML, JSON, XML, TOML out of the box.
*   **Safety Modes:** 
    *   **Strict:** Raises exceptions for missing keys (good for dev/test).
    *   **Non-strict:** Returns a safe wrapper and logs warnings (good for production).
*   **Fallback:** Automatically falls back to the default locale if a key is missing.
*   **Macros:** Define reusable snippets for common patterns (e.g., reusable gender-select ICU snippets).
*   **Powerful CLI:** Generate stubs, lint for missing keys and run a web-based translation studio.

## Installation

> **Requires Python 3.11+**

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
__macros__: # Define a section with macros
    gender: {gender, select, male {He} female {She} other {They}}

greeting: "Hello {}!"
farewell: "Goodbye {name}!"

# Using macros
user_action: "@gender uploaded a new photo."
user_status: "@gender is currently online."

items:
    - name: "Item 1"
    - name: "Item 2"

# Basic key-based pluralization
notifications:
    one: "You have {count} new notification."
    other: "You have {count} new notifications."

# Complex ICU Message Format (Nesting + Select + Plural)
loot_msg: |
  {hero} found {type, select,
      weapon {{count, plural, one {a legendary sword} other {# rusty swords}}}
      potion {{count, plural, one {a healing potion} other {# healing potions}}}
      other {{count} items}
  } in the chest.
```

**2. Access it in Python:**

```python
from doti18n import LocaleData

# Initialize (loads and caches data)
i18n = LocaleData("locales")
en = i18n["en"]

# 1. Standard formatting (Python-style)
print(en.greeting("John"))              # Output: Hello John!
print(en.farewell(name="Alice"))        # Output: Goodbye Alice!

# 2. Raw strings and graceful handling
print(en.farewell)                      # Output: Goodbye {name}! (Raw string)
print(en.farewell())                    # Output: Goodbye ! (Missing var handled)

# 3. Using strings with macros
print(en.user_action(gender="male"))    # Output: He uploaded a new photo.
print(en.user_status(gender="female"))  # Output: She is currently online.

# 4. List access
print(en.items[0].name)                 # Output: Item 1

# 5. Basic Pluralization
print(en.notifications(1))              # Output: You have 1 new notification.
print(en.notifications(5))              # Output: You have 5 new notifications.

# 6. Advanced ICUMF Logic
# "weapon" branch -> "one" sub-branch
print(en.loot_msg(hero="Arthur", type="weapon", count=1))
# Output: Arthur found a legendary sword in the chest.

# "potion" branch -> "other" sub-branch
print(en.loot_msg(hero="Merlin", type="potion", count=5))
# Output: Merlin found 5 healing potions in the chest.
```

## CLI

### Stub Generation / Type Safety
doti18n comes with a CLI to generate type stubs (`.pyi`).

**Why use it?**
1.  **Autocompletion:** Your IDE will suggest available keys as you type.
2.  **Validation:** Static analysis tools will flag errors if you try to access a key that doesn't exist.
3.  **Deep ICUMF Introspection:** The generator parses complex ICUMF strings (like the `loot_msg` example above) and creates precise function signatures.
    *   *Example:* For `loot_msg`, it generates: `def loot_msg(self, *, hero: str, type: str, count: int) -> str`.
    *   Your IDE will tell you exactly which arguments are required, even for deeply nested logic.

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

### Lint
Scan your translation files for missing keys, type mismatches and structural issues across locales.

```bash
# Lint all locales against the default language (en)
doti18n lint locales/

# Lint against a specific source language
doti18n lint locales/ -lang fr
```

### Studio
A web-based translation editor that runs locally.
It lets you browse, edit and save translations in real time from the browser. 
Multiple users can work simultaneously — edits are synced via WebSocket.

Studio requires extra dependencies:
```bash
pip install doti18n[studio]
```

First, create a user:
```bash
doti18n studio add-user admin password
```

Then start the server:
```bash
doti18n studio run locales/
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000), log in, and you'll see all your locales and keys ready to edit.


## Project Status

**Alpha Stage:** The API is stable but may evolve before the 1.0.0 release. Feedback and feature requests are highly appreciated!


## Documentation
Documentation is available at [darkj3suss.github.io/doti18n](https://darkj3suss.github.io/doti18n/).

## License

MIT License. See [LICENSE](https://github.com/darkj3suss/doti18n/blob/main/LICENSE) for details.

## Contact

*   **Issues:** [GitHub Issues](https://github.com/darkj3suss/doti18n/issues)
*   **Direct:** [Telegram](https://t.me/darkjesuss)