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