doti18n supports three formatting styles out of the box. 
You can even mix them in a single string (though consistency is highly recommended).

### Supported Syntax

**1. Python-style** (Curly braces `{}`)

- `"Hello, {}!"` (positional)
- `"Hello, {name}!"` (named)
- `"Balance: {count:.2f}"` (with format spec)

**2. Shell-style** (Dollar sign `$`)

- `"Hello, $name!"`
- `"Hello, ${name}!"`
- `"Hello, $1!"` (positional/indexed)

**3. C-style** (Percent sign `%`)

- `"Hello, %s!"` (positional)
- `"Hello, %(name)s!"` (named)

### Escaping
To use literal characters that are reserved for formatting, double them:

- `{{` and `}}` → `{` and `}`
- `$$` → `$`
- `%%` → `%`

!!! note
    Escaping is only processed when the string is **called** as a function. If accessed as a raw attribute, the string is returned "as-is" (with double characters intact).

---

### Usage Example

`locales/en.yaml`:
```yaml
balance_python: "Your balance is {amount:.2f} dollars."
greeting_c: "Hello, %(name)s!"
farewell_shell: "Goodbye, $name!"
escaped_str: "Literal braces: {{ and }}."
```

**Python Code:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

# 1. Standard Formatting
print(i18n["en"].balance_python(amount=1234.543))   # Output: Your balance is 1234.54 dollars.
print(i18n["en"].greeting_c(name="Alice"))          # Output: Hello, Alice!
print(i18n["en"].farewell_shell(name="Bob"))        # Output: Goodbye, Bob!

# 2. Escaped Characters
print(i18n["en"].escaped_str())                     # Output: Literal braces: { and }.
```

### Missing Variables (Graceful Degradation)
If you omit required variables, doti18n **does not crash**. Instead, it removes the unresolved placeholders from the string.

```python
print(i18n["en"].balance_python())  # Output: Your balance is dollars.
print(i18n["en"].greeting_c())      # Output: Hello, !
```

!!! tip "Type Safety"
    Accessing a key without parentheses (e.g., `i18n["en"].hello`) returns the **raw string**.
    Calling it (e.g., `i18n["en"].hello()`) triggers **formatting**.
    
    To catch forgotten calls or invalid arguments at development time, generate type stubs using the [CLI](../cli/stub.md).