Macros allow you to define reusable text snippets that are replaced across your localization files during the **load-time**. 
This is particularly useful for things like brand names, legal disclaimers, or any frequently repeated text.

## Defining Macros

To define macros, use the special `__macros__` (or `__doti18n__`) key at the top level of your locale file. These keys are automatically removed from the final data after processing.

## Using Macros

Once defined, you can reference a macro anywhere in your strings using the `@` prefix: `@macro_name`

---

## Usage Example

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    __macros__:
      brand: "doti18n"
      author: "darkj3suss"

    welcome: "Welcome to @brand!"
    credits: "Created by @author."
    nested:
      info: "More about @brand."
    ```

=== "JSON"
    `locales/en.json`:
    ```json
    {
        "__macros__": {
            "brand": "doti18n",
            "author": "darkj3suss"
        },
        "welcome": "Welcome to @brand!",
        "credits": "Created by @author.",
        "nested": {
            "info": "More about @brand."
        }
    }
    ```

=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <__macros__>
            <brand>doti18n</brand>
            <author>darkj3suss</author>
        </__macros__>
        <welcome>Welcome to @brand!</welcome>
        <credits>Created by @author.</credits>
        <nested>
            <info>More about @brand.</info>
        </nested>
    </locale>
    ```

=== "TOML"
    `locales/en.toml`:
    ```toml
    [__macros__]
    brand = "doti18n"
    author = "darkj3suss"

    welcome = "Welcome to @brand!"
    credits = "Created by @author."
    
    [nested]
    info = "More about @brand."
    ```

**Python Code:**

```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].welcome)      # Output: Welcome to doti18n!
print(i18n["en"].credits)      # Output: Created by darkj3suss.
print(i18n["en"].nested.info)  # Output: More about doti18n.
```

!!! tip "Performance"
    Since macro replacement happens only once during the loading phase, it has zero performance overhead when you access your translations during runtime.

### Why use Macros?

They are extremely powerful when combined with [ICU Message Format](icumf.md). 
You can use them to avoid repeating complex logic like gender selectors or long templates.

=== "YAML"
    `locales/en.yaml`:
    ```yaml
    __macros__:
      gender: "{gender, select, male {He} female {She} other {They}}"

    user_action: "@gender uploaded a new photo."
    user_status: "@gender is currently online."
    ```

=== "JSON"
    `locales/en.json`:
    ```json
    {
        "__macros__": {
            "gender": "{gender, select, male {He} female {She} other {They}}"
        },
        "user_action": "@gender uploaded a new photo.",
        "user_status": "@gender is currently online."
    }
    ```

=== "XML"
    `locales/en.xml`:
    ```xml
    <locale>
        <__macros__>
            <gender>{gender, select, male {He} female {She} other {They}}</gender>
        </__macros__>
        <user_action>@gender uploaded a new photo.</user_action>
        <user_status>@gender is currently online</user_status>
    </locale>
    ```

=== "TOML"
    `locales/en.toml`:
    ```toml
    __macros__ = {gender = "{gender, select, male {He} female {She} other {They}}"}

    user_action = "@gender uploaded a new photo."
    user_status = "@gender is currently online"
    ```


```python
from doti18n import LocaleData

i18n = LocaleData("locales")

print(i18n["en"].user_action(gender="male"))    # Output: He uploaded a new photo.
print(i18n["en"].user_status(gender="female"))  # Output: She is currently online.
```

---

### Difference from Formatting
While [Formatting](formatting.md) handles dynamic values (like usernames or counts) that change at **run-time**, Macros are for static text known at **load-time**.

| Feature             | Macros                  | Formatting                     |
|:--------------------|:------------------------|:-------------------------------|
| **Syntax**          | `@macro_name`           | `{var}`, `$var`, or `%s`       |
| **When it happens** | Load-time (static)      | Run-time (dynamic)             |
| **Storage**         | Removed from final data | Remains in the string template |
