doti18n provides a fallback mechanism to handle missing translations gracefully. If a requested key is not found in the current locale, doti18n will attempt to retrieve it from a specified fallback locale.


### Configuring Fallback Locale
To set a fallback locale, use the `default_locale` parameter during initialization:

```python
from doti18n import LocaleData

# Initialize with a fallback locale
i18n = LocaleData("locales", default_locale="en")
```

### Fallback Behavior
When a key is missing in the requested locale, doti18n will look for it in the fallback locale (default: "en"). 
If the key exists in the fallback locale, it will return that value. If the key is also missing in the fallback locale, the behavior will depend on whether you are in strict or non-strict mode:
- **Strict mode**, a `KeyError` will be raised indicating that the key is missing in both: the requested and fallback locales.
- **Non-Strict mode**, a `NoneWrapper` will be returned, and a warning will be logged indicating that the key is missing in both locales.

### Example

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    greeting: "Hello!"
    ```

    `locales/fr.yaml`:
    ```yaml
    # Note: 'greeting' key is intentionally missing to demonstrate fallback
    ```

=== "JSON"
    `locales/en.json`:
    ```json
    {
        "greeting": "Hello!"
    }
    ```

    `locales/fr.json`:
    ```json
    {
        // Note: 'greeting' key is intentionally missing to demonstrate fallback
    }
    ```

=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <greeting>Hello!</greeting>
    </locale>
    ```
    
    `locales/fr.xml`:
    ```xml
    <locale>
        <!-- Note: 'greeting' key is intentionally missing to demonstrate fallback -->
    </locale>
    ```

=== "TOML"
    `locales/en.toml`:
    ```toml
    greeting = "Hello!"
    ```
    
    `locales/fr.toml`:
    ```toml
    # Note: 'greeting' key is intentionally missing to demonstrate fallback
    ```

```python
from doti18n import LocaleData
import logging

# Configure logging to capture warnings
logging.basicConfig(level=logging.WARNING)
# Initialize with a fallback locale
i18n = LocaleData("locales", default_locale="en")

# Accessing a key that is missing in 'fr' but exists in 'en'
print(i18n["fr"].greeting)  # Output: Hello!

# You see a warning like that:
# WARNING:LocaleData:Locale 'fr' was not found or root is not a dict or list. (NoneType). Falling back to default locale 'en'.

# Why? Loader found 'fr' locale file, but it's empty, so he just return None to LocaleData
# If 'fr' NON-empty, but 'greeting' key is missing, then the warning will be:
# WARNING:LocaleTranslator['fr']:Fallback for key 'greeting' from 'fr' to 'en'

```
