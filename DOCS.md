# doti18n Documentation

This document provides instructions on how to use the `doti18n` library for internationalization in Python projects.

## Installation

To install the `doti18n` package, you can use pip:

```bash
pip install doti18n
```

## File Structure

Your localization files should be placed in a directory, for example, `locales/`. The library supports `.yml`, `.json`, and `.xml` file formats. Each file should be named with the locale code it represents, e.g., `en.yml`, `fr.json`.

Example directory structure:

```
locales/
├── en.yml
├── fr.json
└── es.xml
```

## Usage

### Initializing the Library

First, you need to initialize the `LocaleData` class with the path to your locales directory and the default locale.

```python
from doti18n import LocaleData

# Initialize LocaleData with the directory containing your localization files
locale_data = LocaleData(locales_dir='locales/', default_locale='en')
```

### Accessing Translations

You can access translations using the `get_translation` method, which returns a `LocaleTranslator` object. You can then access the translation keys as attributes.

```python
# Get the translator for a specific locale
t = locale_data.get_translation('en')

# Access a simple translation
print(t.greeting)  # Output: Hello, World!

# Access a nested translation
print(t.messages.welcome)  # Output: Welcome to our application!
```

### Pluralization

The library supports pluralization based on the count. You need to define the plural forms in your localization files.

**Example `en.yml`:**

```yaml
en:
  apples:
    one: "You have one apple."
    other: "You have {count} apples."
```

**Python code:**

```python
t = locale_data.get_translation('en')

print(t.apples(count=1))  # Output: You have one apple.
print(t.apples(count=5))  # Output: You have 5 apples.
```

### Fallback to Default Locale

If a translation key is not found in the current locale, the library will automatically fall back to the default locale.

**Example `fr.json` (missing `messages.welcome`):**

```json
{
  "fr": {
    "greeting": "Bonjour, le Monde!"
  }
}
```

**Python code:**

```python
t = locale_data.get_translation('fr')

# 'greeting' is present in 'fr.json'
print(t.greeting)  # Output: Bonjour, le Monde!

# 'messages.welcome' is not in 'fr.json', so it falls back to 'en.yml'
print(t.messages.welcome)  # Output: Welcome to our application!
```

### Strict Mode

You can enable strict mode to raise exceptions for missing keys instead of returning `None`.

```python
locale_data = LocaleData(locales_dir='locales/', default_locale='en', strict=True)
t = locale_data.get_translation('en')

try:
    t.non_existent_key
except AttributeError as e:
    print(e)
```
