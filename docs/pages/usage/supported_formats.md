=== "YAML"
    Supports YAML via [PyYAML](https://pyyaml.org/).  
    To enable YAML support, ensure the library is installed with the extra dependency:
    ```bash
    pip install doti18n[yaml]
    ```
    ??? note
        You can also install `PyYAML` separately if doti18n is already installed.
    
    Files must have a `.yaml` or `.yml` extension.

=== "JSON"
    Supports JSON via the built-in `json` module.  
    Included by default; no additional installation required.
    
    Files must have a `.json` extension.

=== "XML"
    Supports XML via the built-in `xml` module.  
    Included by default; no additional installation required.

    Files must have a `.xml` extension.

---

## Structure Examples

=== "YAML"
    `locales/en.yaml`:
    
    ```yaml
    # key-value
    hello: "Hello World!"
    
    # list
    fruits:
        - "Apple"
        - "Banana"
        - "Orange"

    # nested list
    items:
        - name: "Item 1" 
        - name: "Item 2"

    # nested dict
    errors:
        connection: "Connection error occurred."
        timeout: "Request timed out."
    
    # pluralization
    notifications:
        one: "You have {count} new notification."
        other: "You have {count} new notifications."
    ```
    !!! note 
        Standard [YAML features](https://www.yaml.info/learn) (anchors, aliases, complex structures) are fully supported.

=== "JSON"
    `locales/en.json`:
    ```json
    {
        // key-value
        "hello": "Hello World!",
        
        // list
        "fruits": [
            "Apple",
            "Banana",
            "Orange"
        ],        

        // nested list
        "items": [
            {"name": "Item 1"},
            {"name": "Item 2"}
        ],
        
        // nested dict
        "errors": {
            "connection": "Connection error occurred.",
            "timeout": "Request timed out."
        },
        
        // pluralization
        "notifications": {
            "one": "You have {count} new notification.",
            "other": "You have {count} new notifications."
        }
    }
    ```
    !!! note 
        Standard JSON does not support comments. The comments above are for illustration only.

=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <!-- key-value -->
        <hello>Hello World!</hello>
        
        <!-- list -->
        <fruits list="true">
            <fruit>Apple</fruit>
            <fruit>Banana</fruit>
            <fruit>Orange</fruit>
        </fruits>

        <!-- nested list -->
        <items list="true">
            <item>
                <name>Item 1</name>
            </item>
            <item>
                <name>Item 2</name>
            </item>
        </items>
        
        <!-- nested dict -->
        <errors>
            <connection>Connection error occurred.</connection>
            <timeout>Request timed out.</timeout>
        </errors>
        
        <!-- pluralization -->
        <notifications>
            <one>You have {count} new notification.</one>
            <other>You have {count} new notifications.</other>
        </notifications>
    </locale>
    ```
    !!! note "XML Parsing Logic"
        *   **Root Element:** Ignored. You can name it anything (e.g., `<locale>`, `<data>`, `<xml>`), it serves only as a container.
        *   **Lists:** Tags with identical child names are automatically treated as lists.
        *   **Explicit Lists:** To force a list (e.g., for a single element), add the `list="true"` attribute to the parent tag. Using `list="true"` explicitly is recommended for consistency.

---

## Multilocale Files
doti18n supports defining multiple locales in a single file.  

!!! warning 
    Using multilocale files is discouraged as it increases maintenance complexity. Separate files per locale are recommended.

=== "YAML"
    Each document must contain a `locale` key (this key is removed from the final data). Missing keys will trigger an error (or a log in non-strict mode).
    
    `locales/locales.yaml`:
    ```yaml
    locale: "en"
    hello: "Hello World!"
    ---
    locale: "fr"
    hello: "Bonjour le monde!"
    ```
    
    !!! warning
        Any YAML file containing multiple documents (separated by `---`) is treated as a multilocale file.

=== "JSON"
    Each object in the root list must contain a `locale` key (this key is removed from the final data). Missing keys will trigger an error (or a log in non-strict mode).
    
    `locales/locales.json`:
    ```json
    [
        {
            "locale": "en",
            "hello": "Hello World!"
        }, 
        {
            "locale": "fr",
            "hello": "Bonjour le monde!"
        }
    ]
    ```
    
    !!! warning
        Any JSON file where the root element is a **list** is treated as a multilocale file.

=== "XML"
    The root element must be `<locales>`, `<localizations>`, or `<translations>`. Child tags serve as locale names (see example). Incorrect structure will trigger an error (or a log in non-strict mode).
    
    `locales/locales.xml`:
    ```xml
    <locales>
        <en>
            <hello>Hello World!</hello>
        </en>
        <fr>
            <hello>Bonjour le monde!</hello>
        </fr>
    </locales>
    ```
    !!! warning
        Any XML file with a root element named `<locales>`, `<localizations>`, or `<translations>` is treated as a multilocale file.

### Usage Example

```python
from doti18n import LocaleData

i18n = LocaleData("locales")
print(i18n["en"].hello)  # Output: Hello World!
print(i18n["fr"].hello)  # Output: Bonjour le monde!
```