I expect that you already know how to work with these libraries/frameworks, so this guide will focus on integrating doti18n for localization.

## Project structure

All examples have the following project structure:

```text
project_root/
├── locales/
│   ├── en.yaml
│   ├── fr.yaml
│   └── ...
└── main.py
```

## Translation Files

All examples have the following localization file structure:

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    main:
        hello: "Hello World!"
    ```
    `locales/fr.yaml`:
    ```yaml
    main:
        hello: "Bonjour le monde!"
    ```


=== "JSON"
    `locales/en.json`:
    ```json
    {
        "main": {
            "hello": "Hello World!"
        }
    }
    ```
    `locales/fr.json`:
    ```json
    {
        "main": {
            "hello": "Bonjour le monde!"
        }
    }
    ```


=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <main>
            <hello>Hello World!</hello>
        </main>
    </locale>
    ```
    `locales/fr.xml`:
    ```xml
    <locale>
        <main>
            <hello>Bonjour le monde!</hello>
        </main>
    </locale>
    ```

!!! tip "Organization Strategy"
    I highly recommend group related translations by feature or function.
    This structure improves maintainability as your application grows and allows for convenient nested access via dot-notation:
    ```python
    def main(lang: str):
        t = i18n[lang].main
        print(t.hello)
    ```

## Usage & Type Safety

To insure full IDE support (autocompletion and type checking), you should always access translations via the `i18n` object using the locale key. 
This is crucial because `doti18n` relies on generated `.pyi` stubs to provide type information for your specific translation structure.

```python
from doti18n import LocaleData


i18n = LocaleData("locales")


def get_locale():
    # Your logic to determine the locale (e.g., from user settings, request headers, etc.)
    return "en"  # Example: returning "en" for English


def main():
    lang = get_locale()
    
    # Accessing via i18n[lang] allows the IDE to infer properties from .pyi files
    t = i18n[lang].main
    print(t.hello)


if __name__ == "__main__":
    main()
```

### Why this matters?

If you try to pass the translator object directly or use the generic `LocaleTranslator` type, you will lose the specific type safety generated for your locales.

```python
from doti18n import LocaleTranslator

# The IDE or type-chekers won't know that 't.hello' exists or check for typos.
def main(t: LocaleTranslator):
    print(t.hello)
```

Because `LocaleTranslator` is dynamically look up translations at runtime, static analysis tools cannot infer your translation keys unless they are accessed through the typed `i18n` container.
