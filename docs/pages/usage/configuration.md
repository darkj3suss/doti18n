## Strict / Non-Strict Mode

doti18n operates in two modes to accommodate different stages of development and production requirements.

- **Strict Mode**: Raises an exception when accessing a non-existent key or path. This is recommended for development and testing to ensure all translations are present.
- **Non-Strict Mode** (Default): Returns a special `NoneWrapper` object instead of raising an exception. This prevents application crashes by behaving like `None`, while logging a warning to notify developers of the missing translation.

!!! warning "NoneWrapper Behavior"
    `NoneWrapper` behaves like `None`, but is not `None`.
    To check for missing values explicitly, use: `value == None`, or check for truthiness: `if not value:`

### Usage Example

=== "Strict Mode"
    ```python
    from doti18n import LocaleData

    # Initialize in strict mode
    i18n = LocaleData("locales", strict=True)

    try:
        print(i18n["en"].non_existent_key)  # Raises KeyError
    except KeyError as e:
        print(f"Error: {e}") 
        # Output: key/index path 'non_existent_key' not found...
    ``` 

=== "Non-Strict Mode"
    ```python
    import logging
    from doti18n import LocaleData

    # Configure logging to capture warnings
    logging.basicConfig(level=logging.WARNING)

    # Initialize in non-strict mode (default)
    i18n = LocaleData("locales", strict=False)
    
    translation = i18n["en"].non_existent_key
    
    print(translation)  # Output: None
    # Log: WARNING:LocaleTranslator['en']: key/index path 'non_existent_key' not found...
    ```

## Preloading & Manual Loading

doti18n supports preloading to optimize performance. 
When enabled, all locale files in the specified directory are loaded into memory upon initialization.

**Preloading is enabled by default.**

!!! warning
    `preload=True` is the **only** way to load [multilocale files](supported_formats.md#multilocale-files). 
    Attempting to load multilocale configurations via `get_locale()` will result in an error.

### Disabling Preload

To disable preloading, set `preload=False` during initialization. 
You must then load locales manually using the `get_locale()` method.

### Manual Loading Example

Ensure your `locales` directory contains valid translation files (e.g., `en.yaml`, `en.json`, `en.xml`).

**1. Define Locale Files**

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    hello: "Hello World!"
    ```

=== "JSON"
    `locales/en.json`:
    ```json
    {"hello": "Hello World!"}
    ```

=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <hello>Hello World!</hello>
    </locale>
    ```

**2. Load and Access**

```python
from doti18n import LocaleData

# 1. Initialize without preloading
i18n = LocaleData("locales", preload=False)

# 2. Manually load a specific locale
t = i18n.get_locale("en")

# 3. Access translations
print(t.hello)  # Output: Hello World!
```

!!! note 
    When using `get_locale()` method, you don't need to specify file extensions. 
    doti18n automatically detects and loads the appropriate file if it exists and is not loaded yet.
