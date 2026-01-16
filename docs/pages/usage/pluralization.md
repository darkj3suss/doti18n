Pluralization is powered by [Babel](https://babel.pocoo.org/) and follows [CLDR Plural Rules](https://cldr.unicode.org/index/cldr-spec/plural-rules).

To use it:

1.  Define the required forms (e.g., `one`, `few`, `many`, `other`) in your localization file.
2.  Call the key as a function in Python, passing `count` as the first positional argument.

doti18n automatically selects the correct form based on the locale and the count.

## Basic Example

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    cat:
        one: "{count} cat"
        other: "{count} cats"
    ```

=== "JSON"
    `locales/en.json`:
    ```json
    {
        "cat": {
            "one": "{count} cat",
            "other": "{count} cats"
        }
    }
    ```

=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <cat>
            <one>{count} cat</one>
            <other>{count} cats</other>
        </cat>
    </locale>
    ```

**Usage:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].cat(1))   # Output: 1 cat
print(i18n["en"].cat(3))   # Output: 3 cats
print(i18n["en"].cat(11))  # Output: 11 cats
```

## With Variables
You can mix pluralization with variable interpolation. Use standard Python formatting `{variable}` inside the strings and pass values as keyword arguments.

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    cat:
        one: "{count} {color} cat"
        other: "{count} {color} cats"
    ```

=== "JSON"
    `locales/en.json`:
    ```json
    {
        "cat": {
            "one": "{count} {color} cat",
            "other": "{count} {color} cats"
        }
    }
    ```

=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <cat>
            <one>{count} {color} cat</one>
            <other>{count} {color} cats</other>
        </cat>
    </locale>
    ```

**Usage:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].cat(1, color="black"))  # Output: 1 black cat
print(i18n["en"].cat(4, color="white"))  # Output: 4 white cats
print(i18n["en"].cat(7, color="grey"))   # Output: 7 grey cats
```
