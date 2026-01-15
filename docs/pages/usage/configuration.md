## Strict / Non-Strict Mode
doti18n offers two modes of operation to cater to different development and production needs:

- **Strict Mode**: In this mode, any attempt to access a non-existent key or path in the localization data will raise an exception. 
  This is useful during development and testing to ensure that all translations are present and correctly referenced.
- **Non-Strict Mode**: This is the default mode. Instead of raising exceptions for missing keys or paths, doti18n returns a special `NoneWrapper` object. This object behaves like `None` but allows the program to continue running without crashing. 
  Additionally, a warning is logged to inform developers of the missing translation.

!!! warning
    `NoneWrapper` object is not `None`. It only behaves like `None`. If you need to check if the value is None, use `isinstance(value, None)` or `value == None`.





Example:
=== "Strict Mode"
    ```python
    from doti18n import LocaleData

    # Create a LocaleData instance in strict mode
    i18n = LocaleData("locales", strict=True)

    try:
        print(i18n["en"].non_existent_key)  # Raises an exception
    except KeyError as e:
        print(f"Error: {e}")  # Output: key/index path 'non_existent_key' not found in translations (including default 'en'). None will be returned.
    ``` 
=== "Non-Strict Mode"
    ```python
    import logging
    from doti18n import LocaleData

    # Configure logging to see warnings
    logging.basicConfig(level=logging.WARNING)
    # Create a LocaleData instance in non-strict mode (default)
    i18n = LocaleData("locales", strict=False)
    
    translation = i18n["en"].non_existent_key
    
    print(translation)  # Output: None
    # And you see in logs something like:
    # WARNING:LocaleTranslator['en']: key/index path 'non_existent_key' not found in translations (including default 'en'). None will be returned.
    ```

## Preload

doti18n supports preloading of locale files to improve performance and reduce latency when switching languages. 
Preloading allows you to load multiple locale files at once, so they are readily available when needed.
It's enabled by default.

When preloading is enabled, all locale files in the specified directory are loaded into memory during the initialization of the `LocaleData` instance. 
This means that when you access a locale, it is retrieved from memory, resulting in faster access times.

!!! note 
    `preload=True` it's an only way to load multilocale files. You will get an error if try to load multilocale files with method `get_locale()`.

To disable preloading, set the `preload` parameter to `False` when creating the `LocaleData` instance:

```python
from doti18n import LocaleData
i18n = LocaleData("locales", preload=False)
```

When preload disabled, you need to load locales manually using the `get_locale` method.

!!! note
    You need to have directory locale, and file named "en.extension" (like `en.yaml`, `en.json`, `en.xml`, etc.).

=== "YAML"
    ```yaml
    hello: "Hello World!"
    ```

=== "JSON"
    ```json
    {"hello": "Hello World!"}
    ```
=== "XML"
    ```xml
    <locale>
        <hello>Hello World!</hello>
    </locale>
    ```

And use it as follows:
```python
from doti18n import LocaleData
i18n = LocaleData("locales", preload=False)
t = i18n.get_locale("en")
print(t.hello)  # Output: Hello World!
```

