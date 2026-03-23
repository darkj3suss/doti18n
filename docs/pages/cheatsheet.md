**doti18n** is a Python library for accessing localization data (YAML, JSON, XML, TOML) using dot-notation, with built-in type safety, pluralization, macrosing, and ICU Message Format (ICUMF) support.

## Installation

```bash
pip install doti18n        # Default (JSON, XML, TOML)
pip install doti18n[yaml]  # With YAML support
```

## Basic Setup & Access
=== "YAML"
    `locales/en.yaml`:
    ```yaml
    greeting: "Hello World!"
    ```

=== "JSON"
    `locales/en.json`:
    ```json
    {
      "greeting": "Hello World!"
    }
    ```

=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
      <greeting>Hello World!</greeting>
    </locale>
    ```

=== "TOML"
    `locales/en.toml`:
    ```toml
    greeting = "Hello World!"
    ```

**Python Usage:**
```python
from doti18n import LocaleData

i18n = LocaleData("locales")

# Access as raw string
print(i18n["en"].greeting)   # Output: Hello World!
```

---

## File Structure Examples

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

=== "TOML"
    `locales/en.toml`:
    
    ```toml
    # key-value
    hello = "Hello World!"
    
    # list
    fruits = [
        "Apple",
        "Banana",
        "Orange"
    ]

    # nested list
    [[items]]
    name = "Item 1"
    [[items]]
    name = "Item 2"

    # nested dict
    [errors]
    connection = "Connection error occurred."
    timeout = "Request timed out."
    
    # pluralization
    [notifications]
    one = "You have {count} new notification."
    other = "You have {count} new notifications."
    ```

---

## Multilocale

For more information, see [Supported Formats](usage/supported_formats.md#multilocale-files).

=== "YAML"
    `locales/locales.yaml`:
    ```yaml
    __locale__: "en"
    hello: "Hello!"
    ---
    __locale__: "fr"
    hello: "Bonjour!"
    ```

=== "JSON"
    `locales/locales.json`:
    ```json
    [
      {"__locale__": "en", "hello": "Hello!"},
      {"__locale__": "fr", "hello": "Bonjour!"}
    ]
    ```

=== "XML"
    `locales/locales.xml`:
    ```xml
    <locales>
      <en><hello>Hello!</hello></en>
      <fr><hello>Bonjour!</hello></fr>
    </locales>
    ```

=== "TOML"
    `locales/locales.toml`:
    ```toml
    [[locales]]
    __locale__ = "en"
    hello = "Hello!"

    [[locales]]
    __locale__ = "fr"
    hello = "Bonjour!"
    ```

---

## Macros

Macros are resolved **once at load-time**. Use the `__macros__` or `__doti18n__` key and the `@` prefix.  
For more information, see [Macros](usage/macros.md).

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    __macros__:
      brand: "doti18n"

    welcome: "Welcome to @brand!"
    ```

=== "JSON"
    `locales/en.json`:
    ```json
    {
      "__macros__": {
        "brand": "doti18n"
      },
      "welcome": "Welcome to @brand!"
    }
    ```

=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
      <__macros__>
        <brand>doti18n</brand>
      </__macros__>
      <welcome>Welcome to @brand!</welcome>
    </locale>
    ```

=== "TOML"
    `locales/en.toml`:
    ```toml
    welcome = "Welcome to @brand!"

    [__macros__]
    brand = "doti18n"
    ```

**Python Usage:**
```python
print(i18n["en"].welcome)  # Output: Welcome to doti18n!
```

---

## Formatting Styles

Call the key as a function `()` to apply formatting. doti18n supports Python formatting natively.  
For more information, see [Formatting](usage/formatting.md).

!!! tip "Escaping"
    Double the characters to escape them: `{{`, `}}`.

---

## Pluralization

For more information, see [Pluralization](usage/pluralization.md).

=== "YAML"
    ```yaml
    cat:
      one: "{count} cat"
      other: "{count} cats"
    ```

=== "JSON"
    ```json
    {
      "cat": {
        "one": "{count} cat",
        "other": "{count} cats"
      }
    }
    ```

=== "XML"
    ```xml
    <locale>
      <cat>
        <one>{count} cat</one>
        <other>{count} cats</other>
      </cat>
    </locale>
    ```

=== "TOML"
    ```toml
    [cat]
    one = "{count} cat"
    other = "{count} cats"
    ```

**Python Usage:**
```python
print(i18n["en"].cat(1))  # Output: 1 cat
print(i18n["en"].cat(5))  # Output: 5 cats
```

## ICU Message Format (ICUMF)

Powered by CLDR rules. Pass variables as keyword arguments. Use `#` inside sub-numeric formatters to represent the `count`.  
For more information, see [ICU Message Format](usage/icumf.md).

### Plural

=== "YAML"
    ```yaml
    cats: "{count, plural, one {# cat} other {# cats}}"
    ```

=== "JSON"
    ```json
    {
      "cats": "{count, plural, one {# cat} other {# cats}}"
    }
    ```

=== "XML"
    ```xml
    <locale>
      <cats>{count, plural, one {# cat} other {# cats}}</cats>
    </locale>
    ```

=== "TOML"
    ```toml
    cats = "{count, plural, one {# cat} other {# cats}}"
    ```

**Python Usage:**
```python
i18n["en"].cats(count=5)  # Output: 5 cats
```

---

### Select (Switch-case)

=== "YAML"
    ```yaml
    status: "{gender, select, male {He} female {She} other {They}}"
    ```

=== "JSON"
    ```json
    {
      "status": "{gender, select, male {He} female {She} other {They}}"
    }
    ```

=== "XML"
    ```xml
    <locale>
      <status>{gender, select, male {He} female {She} other {They}}</status>
    </locale>
    ```

=== "TOML"
    ```toml
    status = "{gender, select, male {He} female {She} other {They}}"
    ```

**Python Usage:**
```python
i18n["en"].status(gender="female")  # Output: She
```

---

### Selectordinal

=== "YAML"
    ```yaml
    rank: "{pos, selectordinal, one {#st} two {#nd} few {#rd} other {#th}}"
    ```

=== "JSON"
    ```json
    {
      "rank": "{pos, selectordinal, one {#st} two {#nd} few {#rd} other {#th}}"
    }
    ```

=== "XML"
    ```xml
    <locale>
      <rank>{pos, selectordinal, one {#st} two {#nd} few {#rd} other {#th}}</rank>
    </locale>
    ```

=== "TOML"
    ```toml
    rank = "{pos, selectordinal, one {#st} two {#nd} few {#rd} other {#th}}"
    ```

**Python Usage:**
```python
i18n["en"].rank(pos=3)  # Output: 3rd
```

!!! note "Forcing / Disabling ICUMF"
    - **Force:** Prepend `icu:` to a string in your file (e.g., `"icu:My {custom} format"`).
    - **Disable:** Pass `Loader(icumf=False)` when initializing `LocaleData`.

---

## Configuration Modes

Control how doti18n handles missing keys during initialization.  
For more information, see [Configuration](usage/configuration.md#strict-non-strict-mode).

```python
# Non-Strict Mode (Default) - Recommended for Production
i18n = LocaleData("locales", strict=False)
val = i18n["en"].missing_key 
# Returns NoneWrapper (behaves like None), logs a WARNING. Does NOT crash.

# Strict Mode - Recommended for Development/Testing
i18n = LocaleData("locales", strict=True)
val = i18n["en"].missing_key 
# Raises KeyError!
```

---

## CLI Tools

### 1. Type Stubs (`.pyi`)
Generates type definitions for IDE autocompletion and static analysis (mypy).  
For more information, see [Stub Generation](cli/stub.md).

Place section __types__ in the root of your locale file to specify explicit types for variables.
The generator will import these types (if needed) into the stub file.
=== "YAML" 
    `locales/en.yaml`:
    ```yaml
    __types__:
      name: "str"
      user: "app.models.User"

    greeting: "Hello, {name}!"
    user_info: "User {user.name} has email {user.email}."
    ```

=== "JSON" 
    `locales/en.json`:
    ```json
    {
      "__types__": {
        "name": "str",
        "user": "app.models.User"
      },
      "greeting": "Hello, {name}!",
      "user_info": "User {user.name} has email {user.email}."
    }
    ```
=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
      <__types__>
        <name>str</name>
        <user>app.models.User</user>
      </__types__>
      <greeting>Hello, {name}!</greeting>
      <user_info>User {user.name} has email {user.email}.</user_info>
    </locale>
    ```
=== "TOML"
    `locales/en.toml`:
    ```toml
    greeting = "Hello, {name}!"
    user_info = "User {user.name} has email {user.email}."
    [__types__]
    name = "str"
    user = "app.models.User"
    ```

!!! warning "Virtual Environment"
    Always run the stub generator inside your project's **venv**. It writes directly to the installed package directory.

```bash
doti18n stub locales/           # Generate stubs (default source: 'en')
doti18n stub locales/ --lang fr # Use 'fr' as the source of truth
doti18n stub --clean            # Remove generated stubs
```

### 2. Linter
Checks for missing keys, type mismatches, and list length differences between locales.  
For more information, see [Linting Translations](cli/lint.md).

```bash
doti18n lint locales/             # Lint against 'en' (default)
doti18n lint locales/ --source fr # Lint against 'fr'
doti18n lint locales/ --icumf     # Enable ICU syntax validation
```

### 3. Studio
A web-based translation editor. Multiple users can edit translations simultaneously with real-time sync.  
For more information, see [Studio](cli/studio.md).

```bash
pip install doti18n[studio]              # Install studio dependencies
doti18n studio add-user admin mypassword # Create a user
doti18n studio run locales/              # Start the editor on http://127.0.0.1:5000
```

---

## Advanced Customization
- **[Custom Formatters](usage/icumf.md#custom-formatters):** Inherit from `BaseFormatter`.
- **[Custom Loaders](usage/custom_loaders.md):** Inherit from `BaseLoader`.
- **[Custom Tag Handling (HTML to Markdown, etc.)](usage/icumf.md#tags-html-support):** Pass `tag_formatter=MarkdownFormatter()` to the `ICUMF` configuration. 
                                                           Or call keys with `formatter=MarkdownFormatter()` to apply Markdown formatting at runtime.

!!! warning "Execution Order"
    Custom loaders and formatters must be defined/imported **before** initializing `LocaleData`(or `Loader`/`ICUMF`).