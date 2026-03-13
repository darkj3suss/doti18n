doti18n supports python-style formatting out of the box.

### Supported Syntax

**Python-style** (Curly braces `{}`)

- `"Hello, {}!"` (positional)
- `"Hello, {name}!"` (named)
- `"Balance: {count:.2f}"` (with format spec)


!!! note
    Escaping is only processed when the string is **called** as a function. If accessed as a raw attribute, the string is returned "as-is" (with double characters intact).

---

### Usage Example

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    balance_python: "Your balance is {amount:.2f} dollars."
    hello: "Hello, {name}!"
    escaped_str: "Literal braces: {{ and }}."
    ```

=== "JSON"
    `locales/en.json`:
    ```json
    {
        "balance_python": "Your balance is {amount:.2f} dollars.",
        "hello": "Hello, {name}!",
        "escaped_str": "Literal braces: {{ and }}."
    }
    ```

=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <balance_python>Your balance is {amount:.2f} dollars.</balance_python>
        <hello>Hello, {name}!</hello>
        <escaped_str>Literal braces: {{ and }}.</escaped_str>
    </locale>
    ```

=== "TOML"
    `locales/en.toml`:
    ```toml
    balance = "Your balance is {amount:.2f} dollars."
    hello = "Hello, {name}!"
    escaped_str = "Literal braces: {{ and }}."
    ```

**Python Code:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

# 1. Standard Formatting
print(i18n["en"].balance_python(amount=1234.543))   # Output: Your balance is 1234.54 dollars.
print(i18n["en"].hello(name="Alice"))               # Output: Hello, Alice!

# 2. Escaped Characters
print(i18n["en"].escaped_str())                     # Output: Literal braces: { and }.
```

### Missing Variables (Graceful Degradation)
If you omit required variables, doti18n **does not crash**. Instead, it removes the unresolved placeholders from the string.

```python
print(i18n["en"].balance_python())  # Output: Your balance is dollars.
print(i18n["en"].hello)             # Output: Hello, !
```

!!! tip "Type Safety"
    Accessing a key without parentheses (e.g., `i18n["en"].hello`) returns the **raw string**.
    Calling it (e.g., `i18n["en"].hello()`) triggers **formatting**.
    
    To catch forgotten calls or invalid arguments at development time, generate type stubs using the [CLI](../cli/stub.md).