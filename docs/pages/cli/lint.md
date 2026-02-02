## Description
The CLI tool scans your translation files for consistency issues.
It compares all target locales against a "source of truth" (default is `en`) to detect missing keys, type mismatches, and structural differences.

## Example
Given the following structure:

```text
project_root/  
├── locales/  
│   ├── en.yaml
│   └── fr.yaml
└── main.py  
```

Content of `en.yaml` (Source):
```yaml
greeting: "Hello, World!"
menu:
  save: "Save"
  open: "Open"
items:
  - "Apple"
  - "Banana"
```

Content of `fr.yaml` (Target with errors):
```yaml
# 'greeting' is missing
menu: "Menu" # Type mismatch: expected dict, got string
items:
  - "Pomme"
  # List length mismatch (missing 2nd item)
```

Run the linter:
```bash
doti18n lint locales/
```

### Results

**Consistency Checks:**
The tool outputs logs indicating specific issues within your locale files.

*Missing Keys:*
Detects keys that exist in the source locale but are absent in the target.

```text
[fr] Missing key: greeting
[fr] Missing key: menu.save
[fr] Missing key: menu.open
```

---
*Type Mismatches:*
Ensures data types (strings, lists, dictionaries) are consistent across languages.

```text
[fr] Type mismatch at menu: expected dict, got str
```

---
*List Integrity:*
Verifies that lists have the same length and structure.

```text
[fr] List length mismatch at items: expected 2, got 1
```

## Options

**Set source of truth:**
Specify which locale code should be used as the reference for validation (default is `en`).
```bash
doti18n lint locales/ --source fr
```

**Check ICU Syntax:**
Enable validation for ICU MessageFormat syntax (e.g., checking braces and placeholders).
```bash
doti18n lint locales/ --icumf
```