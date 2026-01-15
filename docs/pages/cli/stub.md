## Description
The CLI tool generates type stubs (`.pyi`) based on your translation files. 
This enables static type checking and IDE autocompletion for keys and string formatting arguments.

## Example
Given the following structure:

```text
project_root/  
├── locales/  
│   └── en.yaml  
└── main.py  
```

Content of `en.yaml`:
```yaml
greeting: "Hello, {name}!"
basket: "You have {0} bananas, {1} apples, and {2} oranges in your basket."
```

Run the generator:
```bash
doti18n stub locales/
```

!!! note
    Stubs must be regenerated after any changes to localization files (adding keys, changing arguments, etc.).

### Results

**Autocompletion:**
Your IDE will now suggest available keys and methods.

<video width="80%" autoplay loop muted playsinline>
  <source src="/doti18n/assets/images/stub.mp4" type="video/mp4">
  Your browser doesn't support video
</video>

**Static Analysis:**
Type checkers (like mypy) will detect errors such as typos or mismatched formatting arguments.

*Typos:*

![example](../assets/images/stub1.png)  

---
*Unexpected arguments:*

![example](../assets/images/stub2.png)

---
*Missing arguments:*

![example](../assets/images/stub3.png)

![example](../assets/images/stub4.png)


!!! warning "Virtual Environment"
    The generator writes the `__init__.pyi` file directly into the installed `doti18n` package directory.  
    **Always run this command inside a virtual environment [(venv)](https://docs.python.org/3/library/venv.html).** Modifying system-wide Python packages is strongly discouraged.


## Options

**Clean stubs:**
Remove previously generated type definitions.
```bash
doti18n stub --clean
```

**Set default locale:**
Specify which locale file should be used as the source of truth for generating types (default is `en`).
```bash
doti18n stub locales/ --lang fr
```