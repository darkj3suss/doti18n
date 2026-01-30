ICU Message Format (ICUMF) is powered by its own parser and formatter within doti18n. For pluralization, it follows [CLDR Plural Rules](https://cldr.unicode.org/index/cldr-spec/plural-rules), which are powered by [Babel](https://babel.pocoo.org/).

## Syntax
ICUMF uses a specific syntax for defining messages, including pluralization, selection, and variable interpolation.

- **Variable Interpolation**: `{variable}`
- **Hash**: In sub-numeric formatters (`plural`, `selectordinal`), `#` represents the `count` value.
- **Pluralization**: `{variable, plural, one {singular form} other {plural form}}`
- **Selectordinal**: `{variable, selectordinal, one {1st form} two {2nd form} few {3rd form} other {default form}}`
- **Select**: `{variable, select, option1 {text1} option2 {text2} other {default text}}`
- **Formatters**: `{variable, formatter, style}` (e.g., for dates).
- **Escaping**: Use single quotes `'` to escape the next character. To include a literal single quote, use two single quotes `''`.
- **Nesting**: ICUMF supports nested constructs for complex messages.
- **Whitespace**: Ignored outside of the message text.

## Basic Example

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    cat: "I have {count, plural, one {# cat} other {# cats}}"
    ```
=== "JSON"
    `locales/en.json`:
    ```json
    {
        "cat": "I have {count, plural, one {# cat} other {# cats}}"
    }
    ```
=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <cat>I have {count, plural, one {# cat} other {# cats}}</cat>
    </locale>
    ```

**Usage:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].cat(count=1))   # Output: I have 1 cat
print(i18n["en"].cat(count=3))   # Output: I have 3 cats
print(i18n["en"].cat(count=11))  # Output: I have 11 cats
```

Вот готовая секция **Manage ICUMF** для файла `icumf.md`. Я написал её в том же стиле, что и остальные документы: с примерами кода и объяснением параметров.

Вставь это в конец файла `icumf.md`.

---

## Manage ICUMF

By default, doti18n automatically enables ICUMF parsing with standard settings. However, you can customize its behavior, adjust performance settings, or disable it entirely.

To do this, you need to manually configure the `Loader` and inject it into `LocaleData`.

### Disabling ICUMF
If you don't use ICUMF features and want to avoid the parsing overhead, or if your strings contain characters that conflict with ICUMF syntax (like `{}` used for other purposes), you can disable it.

```python
from doti18n import LocaleData
from doti18n.loaders import Loader

# 1. Create a loader with ICUMF disabled
loader = Loader(icumf=False)

# 2. Inject the loader into LocaleData
i18n = LocaleData("locales", loader=loader)
```

### Forcing ICUMF
If for some reason ICUMF doesn't parse your strings automatically (e.g., due to conflicts with other formatting styles), you can force-enable it via marking strings in your localization files.
This `icu:` prefix tells doti18n to always treat the string as ICUMF. doti18n will delete the prefix before parsing.

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    cat: "icu:I have {count, plural, one {# cat} other {# cats}}"
    ```
=== "JSON"
    `locales/en.json`:
    ```json
    {
        "cat": "icu:I have {count, plural, one {# cat} other {# cats}}"
    }
    ```
=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <cat>icu:I have {count, plural, one {# cat} other {# cats}}</cat>
    </locale>
    ```

### Advanced Configuration
To adjust the cache size or parser behavior, you need to create an `ICUMF` instance manually and pass it to the loader.

```python
from doti18n import LocaleData
from doti18n.loaders import Loader
from doti18n.icumf import ICUMF

# 1. Configure ICUMF
icumf = ICUMF(
    cache_size=2048,      # Increase cache for rendered strings
    strict=True,          # Enforce strict validation
    
    # Parser options (passed via kwargs)
    depth_limit=20,       # Limit nesting depth
    allow_tags=False,     # Disable HTML-like tag parsing
    require_other=False   # Don't require 'other' in plural/selectordinal (not recommended, it may break doti18n logic)
)

# 2. Create Loader with custom ICUMF
loader = Loader(icumf=icumf)

# 3. Initialize LocaleData
i18n = LocaleData("locales", loader=loader)
```

### Parser Parameters
These parameters are passed as keyword arguments (`**kwargs`) to the `ICUMF` constructor and control the internal `Parser`.

| Parameter                | Type   | Default | Description                                                                                   |
|:-------------------------|:-------|:--------|:----------------------------------------------------------------------------------------------|
| `cache_size`             | `int`  | `1024`  | The maximum number of rendered strings to keep in memory (LRU Cache).                         |
| `depth_limit`            | `int`  | `50`    | Maximum recursion depth for nested messages. Prevents stack overflow on malformed strings.    |
| `allow_tags`             | `bool` | `True`  | Enables parsing of HTML/XML-like tags (e.g., `<b>Bold</b>`).                                  |
| `strict_tags`            | `bool` | `True`  | If `True`, ensures that closing tags match opening tags (e.g., `<b>...</i>` raises an error). |
| `tag_prefix`             | `str`  | `None`  | If set, only tags starting with this prefix are parsed.                                       |
| `require_other`          | `bool` | `True`  | If `True`, requires an `other` option in `plural`, `select`, and `selectordinal` formats.     |
| `allow_format_spaces`    | `bool` | `True`  | Allows whitespace inside format arguments (e.g., `{ count, plural, ... }`).                   |


## Variable Interpolation
If you want to include additional variables in your messages, simply add them to the message string and pass them as keyword arguments.

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    greeting: "Hello, {name}! You have {count, plural, one {# new message} other {# new messages}}."
    ```
=== "JSON"
    `locales/en.json`:
    ```json
    {
        "greeting": "Hello, {name}! You have {count, plural, one {# new message} other {# new messages}}."
    }
    ```
=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <greeting>Hello, {name}! You have {count, plural, one {# new message} other {# new messages}}.</greeting>
    </locale>
    ```

**Usage:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].greeting(name="Alice", count=1))   # Output: Hello, Alice! You have 1 new message.
print(i18n["en"].greeting(name="Bob", count=5))     # Output: Hello, Bob! You have 5 new messages.
```

!!! note 
    If your ICUMF string contains **only** variable interpolation (without pluralization or formatters), it won't be processed as ICUMF. 
    Instead, it will use standard Python formatting (`str.format()`).

## Pluralization and Selectordinal
ICUMF supports pluralization using the `plural` and `selectordinal` formats. You can define different message forms based on the numeric value of a variable.

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    item_count: "You have {count, plural, one {# item} other {# items}} in your cart."
    rank: "You are ranked {position, selectordinal, one {#st} two {#nd} few {#rd} other {#th}} in the competition."
    ```
=== "JSON"
    `locales/en.json`:
    ```json
    {
        "item_count": "You have {count, plural, one {# item} other {# items}} in your cart.",
        "rank": "You are ranked {position, selectordinal, one {#st} two {#nd} few {#rd} other {#th}} in the competition."
    }
    ```
=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <item_count>You have {count, plural, one {# item} other {# items}} in your cart.</item_count>
        <rank>You are ranked {position, selectordinal, one {#st} two {#nd} few {#rd} other {#th}} in the competition.</rank>
    </locale>
    ```

**Usage:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].item_count(count=1))    # Output: You have 1 item in your cart.
print(i18n["en"].item_count(count=4))    # Output: You have 4 items in your cart.

print(i18n["en"].rank(position=1))       # Output: You are ranked 1st in the competition.
print(i18n["en"].rank(position=2))       # Output: You are ranked 2nd in the competition.
print(i18n["en"].rank(position=3))       # Output: You are ranked 3rd in the competition.
print(i18n["en"].rank(position=4))       # Output: You are ranked 4th in the competition.
```

## Select
The `select` format allows you to define different message forms based on exact string matches (similar to a switch-case statement).

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    user_status: "{status, select, active {Welcome back!} inactive {Please activate your account.} banned {Your account is banned.} other {Hello, guest!}}"
    gender_greeting: "{gender, select, male {Hello, sir!} female {Hello, miss!} other {Hello!}}"
    ```
=== "JSON"
    `locales/en.json`:
    ```json
    {
        "user_status": "{status, select, active {Welcome back!} inactive {Please activate your account.} banned {Your account is banned.} other {Hello, guest!}}",
        "gender_greeting": "{gender, select, male {Hello, sir!} female {Hello, miss!} other {Hello!}}"
    }
    ```
=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <user_status>{status, select, active {Welcome back!} inactive {Please activate your account.} banned {Your account is banned.} other {Hello, guest!}}</user_status>
        <gender_greeting>{gender, select, male {Hello, sir!} female {Hello, miss!} other {Hello!}}</gender_greeting>
    </locale>
    ```

**Usage:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].user_status(status="active"))    # Output: Welcome back!
print(i18n["en"].user_status(status="inactive"))  # Output: Please activate your account.
print(i18n["en"].user_status(status="banned"))    # Output: Your account is banned.
print(i18n["en"].user_status(status="other"))     # Output: Hello, guest!

print(i18n["en"].gender_greeting(gender="male"))    # Output: Hello, sir!
print(i18n["en"].gender_greeting(gender="female"))  # Output: Hello, miss!
print(i18n["en"].gender_greeting(gender="other"))   # Output: Hello!
```

## Formatters
Out of the box, doti18n supports the `date` formatter. You can also implement custom formatters by extending the `BaseFormatter` class. See the [Custom Formatters](#custom-formatters) section for details.

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    appointment: "Your appointment is on {date, date, short}."
    now: "Current date and time: {now, date, long}."
    custom: "Custom formatted date: {date, date, %A, %d %B %Y year, %H:%M:%S (%Z)}."
    ```
=== "JSON"
    `locales/en.json`:
    ```json
    {
        "appointment": "Your appointment is on {date, date, short}.",
        "now": "Current date and time: {now, date, long}.",
        "custom": "Custom formatted date: {date, date, %A, %d %B %Y year, %H:%M:%S (%Z)}."
    }
    ```
=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <appointment>Your appointment is on {date, date, short}.</appointment>
        <now>Current date and time: {now, date, long}.</now>
        <custom>Custom formatted date: {date, date, %A, %d %B %Y year, %H:%M:%S (%Z)}.</custom>
    </locale>
    ```

**Usage:**

```python
from doti18n import LocaleData
from datetime import datetime
from zoneinfo import ZoneInfo

i18n = LocaleData("locales")
now = datetime.now(tz=ZoneInfo("UTC"))

print(i18n["en"].appointment(date=now))  # Output: Your appointment is on 29.01.2026.
print(i18n["en"].now(now=now))           # Output: Current date and time: 29.01.2026 22:30:19.
print(i18n["en"].custom(date=now))       # Output: Custom formatted date: Thursday, 29 January 2026 year, 22:30:19 (UTC).
```

## Escaping
To include literal characters that are reserved for ICUMF formatting (like `{` or `}`), use single quotes `'` to escape the sequence. To include a single quote itself, use two single quotes `''`.

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    escaped: "This is a literal brace: '{' and this is a single quote: ''."
    ```
=== "JSON"
    `locales/en.json`:
    ```json
    {
        "escaped": "This is a literal brace: '{' and this is a single quote: ''."
    }
    ```
=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <escaped>This is a literal brace: '{' and this is a single quote: ''.</escaped>
    </locale>
    ``` 

**Usage:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].escaped())  # Output: This is a literal brace: { and this is a single quote: '.
```

## Nesting
ICUMF supports nesting constructs to build complex logic. You can place pluralization, select, and other formats inside each other.

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    backpack: |
        You have {item, select,
            book {{count, plural, one {# book} other {# books}}} 
            pen {{count, plural, one {# pen} other {# pens}}} 
            other {{count} items}
        } in your backpack.
    ```
=== "JSON"
    `locales/en.json`:
    ```json
    {
        "backpack": "You have {item, select, book {{count, plural, one {# book} other {# books}}} pen {{count, plural, one {# pen} other {# pens}}} other {{count} items}} in your backpack."
    }
    ```
=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <backpack>You have {item, select, 
                      book {{count, plural, one {# book} other {# books}}} 
                      pen {{count, plural, one {# pen} other {# pens}}} 
                      other {{count} items}
                      } in your backpack.
        </backpack>
    </locale>
    ```

!!! note "Important: Variable Context"
    Notice the `other` option in the example above. Inside `other`, we use `{count}` instead of `#`.
    
    The hash symbol (`#`) represents the count **only** within sub-numeric formatters (like `plural` or `selectordinal`). Since `select` is not numeric, you must use the standard `{count}` interpolation variable there.

**Usage:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].backpack(item="book", count=1))    # Output: You have 1 book in your backpack.
print(i18n["en"].backpack(item="book", count=3))    # Output: You have 3 books in your backpack.
print(i18n["en"].backpack(item="pen", count=1))     # Output: You have 1 pen in your backpack.
print(i18n["en"].backpack(item="pen", count=5))     # Output: You have 5 pens in your backpack.

# This uses the 'other' case.
print(i18n["en"].backpack(item="sword", count=10))  # Output: You have 10 items in your backpack.
```

## Whitespaces
ICUMF ignores whitespace characters (spaces, tabs, newlines) outside of the message text. You can format your ICUMF strings for better readability without affecting the logic.

However, be careful when using multi-line strings in YAML or XML, as indentation inside the message string itself (e.g., inside `{...}`) might be preserved depending on how the file is parsed.

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    cart: "You have {count, plural, one {  # item  } other {  # items  }} in your cart."
    ```
=== "JSON"
    `locales/en.json`:
    ```json
    {
        "cart": "You have {count, plural, one {  # item  } other {  # items  }} in your cart."
    }
    ```
=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <cart>You have {count, plural, one {  # item  } other {  # items  }} in your cart.</cart>
    </locale>
    ```

**Usage:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].cart(count=1))   # Output: You have   1 item   in your cart.
print(i18n["en"].cart(count=4))   # Output: You have   4 items   in your cart.
```

As seen above, the extra spaces explicitly placed inside the plural forms (`{  # item  }`) are preserved in the output.

## Custom Formatters

### Requirements
To create a custom formatter, define a class that inherits from `doti18n.icumf.formatter.BaseFormatter` and meets these criteria:

1. **`name`**: A string representing the formatter's name (e.g., `"crypto"`).
2. **`is_subnumeric`**: Boolean. True if the formatter logic depends on a numeric count (like `plural`).
3. **`is_submessage`**: Boolean. True if the formatter contains nested messages (like `select`).
4. **`__init__`**: Must accept a `strict: bool` argument.
5. **`__call__`**: Must implement the formatting logic and accept/return parameters as defined in the parent class.

### Example Implementation

!!! tip
    If you are unsure how to implement a sub-numeric or sub-message formatter, refer to the source code of built-in formatters in the `doti18n.icumf.formatters` module.

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    crypto: "You have {value, crypto, usdt} in your wallet."
    ```
=== "JSON"
    `locales/en.json`:
    ```json
    {
        "crypto": "You have {value, crypto, usdt} in your wallet."
    }
    ```
=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <crypto>You have {value, crypto, usdt} in your wallet.</crypto>
    </locale>
    ```

```python
from doti18n import LocaleData
from doti18n.icumf.formatters import BaseFormatter
from doti18n.icumf.nodes import Node, FormatNode, TextNode
from typing import Sequence, Optional
# import some_external_crypto_library as clib

class CryptoFormatter(BaseFormatter):
    name = "crypto"
    is_subnumeric = False
    is_submessage = False

    def __init__(self, strict: bool = False):
        self._strict = strict

    def __call__(self, t: "LocaleTranslator", node: Node, **kwargs) -> Sequence[Optional[Node]]:
        if not isinstance(node, FormatNode):
            raise TypeError("CryptoFormatter can only process FormatNode instances.")
        
        value = kwargs.get(node.name)
        if value is None:
            if self._strict:
                raise ValueError(f"Missing value for '{node.name}' in CryptoFormatter.")
            else:
                return []  # Return empty for graceful degradation
        
        # Assume clib.format converts coins to the style (e.g., USDT)
        # formatted_value = clib.format(value, node.style)
        formatted_value = "84467,51" # Mock result
        
        return [TextNode(f"{formatted_value} {node.style.upper()}")]

# Register formatter (by defining/importing it) BEFORE LocaleData initialization
i18n = LocaleData("locales")

print(i18n["en"].crypto(value="123 BTC"))  # Output: You have 84467,51 USDT in your wallet.
```

!!! warning "Execution Order"
    You **must** define or import your custom formatter **before** creating the `LocaleData` or `Loader` instance.
    
    **Why?** The ICUMF manager registers all available formatters at initialization. If your custom formatter is defined later, it won't be registered.

## Tags & HTML Support

doti18n's parser supports XML/HTML-like tags out of the box. By default, they are rendered "as is" (useful for web apps), but you can intercept and transform them — for example, to convert HTML tags into Markdown for Telegram bots or console output.
You also can implent your own tag formatter (see [custom formatters](icumf.md#custom-formatters)) to handle custom tags or give it in another format.

### Basic Usage
Tags are parsed as structured nodes, not just text. This ensures that opening and closing tags match (unless `strict_tags=False`).

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    welcome: "Welcome, <b>{name}</b>! Click <link>here</link>."
    ```

**Usage (Default HTML behavior):**
```python
print(i18n["en"].welcome(name="User"))
# Output: Welcome, <b>User</b>! Click <link>here</link>.
```

### Custom Tag Processing (HTML to Markdown)
To transform tags, you need to implement a custom formatter (or use built-in) class and inject it into the `ICUMF` configuration via the `tag_formatter` argument.

The formatter receives a `TagNode` which contains `children` (the content inside the tag).

**Example: Converting `<b>` to `**` and `<i>` to `__`**

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    msg: "Hello <b>{name}</b>, this is <i>italic</i>."
    ```
=== "JSON"
    `locales/en.json`:
    ```json
    {
        "msg": "Hello <b>{name}</b>, this is <i>italic</i>."
    }
    ```
=== "XML"
    !!! warning "XML Limitation"
        Tag support is not implemented in XML


```python
from doti18n import LocaleData
from doti18n.loaders import Loader
from doti18n.icumf import ICUMF
from doti18n.icumf.formatters import MarkdownFormatter

# Initialize ICUMF with the custom tag formatter
icumf = ICUMF(tag_formatter=MarkdownFormatter)
loader = Loader(icumf=icumf)
i18n = LocaleData("locales", loader=loader)

print(i18n["en"].msg(name="Alice"))  # Output: Hello **Alice**, this is __italic__.
```

!!! tip "Nested Tags"
    Since the formatter returns the original `node.children`, doti18n continues to process the content inside the tag. This means nesting (e.g., `<b><i>Text</i></b>`) works automatically with your custom formatter.