## Installation 

Install from [PyPI](https://pypi.org/project/doti18n/):

```bash
pip install doti18n
```

For **YAML** support, install the extra dependency:

```bash
pip install doti18n[yaml]
```

Or install from source:

```bash
git clone https://github.com/darkj3suss/doti18n
cd doti18n
pip install .
```

## First Steps
Create a directory for your localization files.

!!! tip
    doti18n supports YAML, JSON, and XML out of the box. You can add other formats via [Custom Loaders](usage/custom_loaders.md).

**Directory Structure:**

```
project_root/
├── locales/
│   ├── en.yaml
│   ├── fr.yaml
│   └── ...
└── main.py
```

### Create Files

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    hello: "Hello World!"
    ```
    `locales/fr.yaml`:
    ```yaml
    hello: "Bonjour le monde!"
    ```

=== "JSON"
    `locales/en.json`:
    ```json
    {"hello": "Hello World!"}
    ```
    `locales/fr.json`:
    ```json
    {"hello": "Bonjour le monde!"}
    ```

=== "XML"
    !!! note
        The root element is ignored in XML files. See [Supported Formats](usage/supported_formats.md#__tabbed_2_3) for details.

    `locales/en.xml`:
    ```xml
    <locale>
        <hello>Hello World!</hello>
    </locale>
    ```
    `locales/fr.xml`:
    ```xml
    <locale>
        <hello>Bonjour le monde!</hello>
    </locale>
    ```

---

### Usage

Load and access translations using dot-notation:

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].hello)  # Output: Hello World!
print(i18n["fr"].hello)  # Output: Bonjour le monde!
```

That's it! 
Check the [Usage](usage/supported_formats.md) section for advanced features like pluralization, formatting, and strict mode.