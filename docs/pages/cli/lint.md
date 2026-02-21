## What is it?
A CLI tool that scans your translation files for any issues. 
It compares all locales against your "source of truth" (default is `en`) to find missing keys, type mismatches, and other structural mess-ups.

## Example
Imagine you have this structure:

```text
project_root/  
├── locales/  
│   ├── en.yaml
│   └── fr.yaml
└── main.py  
```

`en.yaml` (Original):
```yaml
greeting: "Hello, World!"
menu:
  save: "Save"
  open: "Open"
items:
  - "Apple"
  - "Banana"
placeholder: "Hello {name}!"
```

`fr.yaml` (Translation with errors):
```yaml
# 'greeting' is missing
menu: "Menu" # Type mismatch: expected dict, got string
items:
  - "Pomme"
  # List length mismatch (missing the 2nd element)
placeholder: "Bonjour" # Missing placeholder {name}
extra_key: "Why am I here if I'm not in the original?" # Extra key
```

Run the lint:
```bash
doti18n lint locales/
```

### Check Results

**Core Checks:**
The tool will spit out a log with all the problems found.

*Missing Keys:*
Finds stuff that exists in the original but is missing in the translation.

```text
[fr] Missing key: greeting
[fr] Missing key: menu.save
[fr] Missing key: menu.open
```

---
*Type Mismatches:*
Ensures that data types (strings, lists, dicts) match everywhere.

```text
[fr] Type mismatch at menu: expected dict, got str
```

---
*List Integrity:*
Checks list lengths and their structure.

```text
[fr] List length mismatch at items: expected 2, got 1
```

---
*Extra Keys:*
If there are keys in the translation that don't exist in the original, the linter will give you a warning.

```text
[fr] Extra key: extra_key
```

---
*Placeholder Validation (Formatted Strings):*
The linter automatically checks that you haven't forgotten any variables.

```text
[fr] Missing format fields at some_key: name
```

## Options

**Change the Source of Truth:**
You can specify a different locale as the reference (default is `en`).
```bash
doti18n lint locales/ --source fr
```

**ICU MessageFormat Validation:**
If you're using ICU (plurals, selects, etc.), add this flag for deep syntax checking, tag validation, and placeholder matching inside ICU messages.
```bash
doti18n lint locales/ --icumf
```