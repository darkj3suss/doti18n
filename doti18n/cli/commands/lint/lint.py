import logging
from typing import Optional

from doti18n.icumf import ICUMF, html_pattern, icumf_pattern
from doti18n.icumf.nodes import FormatNode, MessageNode, TagNode

from ..stub.formatted_stub import PLACEHOLDER_REGEX

logger = logging.getLogger("doti18n.lint")
PROBLEMS = 0


def _lint(locale_code: str, locale_data: dict, source_data: dict, path: str = "", icumf: Optional[ICUMF] = None):
    global PROBLEMS
    if isinstance(locale_data, dict) and isinstance(source_data, dict):
        lint_dict(locale_code, locale_data, source_data, path, icumf)
    elif isinstance(locale_data, list) and isinstance(source_data, list):
        _lint_list(locale_code, locale_data, source_data, path, icumf)
    else:
        if type(locale_data) is not type(source_data):
            logger.error(
                f"[{locale_code}] Type mismatch at {path}: "
                f"expected {type(source_data).__name__}, got {type(locale_data).__name__}"
            )
            PROBLEMS += 1
        else:
            if isinstance(source_data, str) and isinstance(locale_data, str):
                if source_data.strip() == "" and locale_data.strip() != "":
                    logger.warning(f"[{locale_code}] Non-empty translation for empty source at {path}")
                    PROBLEMS += 1

                is_icu_like = (
                    source_data.startswith("icu:")
                    or locale_data.startswith("icu:")
                    or icumf_pattern.search(source_data)
                    or icumf_pattern.search(locale_data)
                    or html_pattern.search(source_data)
                    or html_pattern.search(locale_data)
                )
                if is_icu_like and icumf:
                    _lint_icumf(locale_code, locale_data, source_data, path, icumf)
                elif not is_icu_like:
                    _lint_formatted(locale_code, locale_data, source_data, path)


def _lint_icumf(locale_code: str, locale_data: str, source_data: str, path: str, icumf: ICUMF):
    global PROBLEMS
    source_ast = icumf.get_ast(source_data)
    locale_ast = icumf.get_ast(locale_data)

    if source_ast is None or locale_ast is None:
        return

    def extract_info(nodes, vars_set, tags_set):
        for node in nodes:
            if isinstance(node, (FormatNode, MessageNode)):
                if not node.is_hash:
                    vars_set.add(node.name)
                if isinstance(node, MessageNode):
                    for option_nodes in node.options.values():
                        extract_info(option_nodes, vars_set, tags_set)
            elif isinstance(node, TagNode):
                tags_set.add(node.name)
                extract_info(node.children, vars_set, tags_set)

    source_vars: set[str] = set()
    source_tags: set[str] = set()
    extract_info(source_ast, source_vars, source_tags)

    locale_vars: set[str] = set()
    locale_tags: set[str] = set()
    extract_info(locale_ast, locale_vars, locale_tags)

    missing_vars = source_vars - locale_vars
    extra_vars = locale_vars - source_vars

    if missing_vars:
        logger.error(f"[{locale_code}] Missing placeholders at {path}: {', '.join(missing_vars)}")
        PROBLEMS += 1

    if extra_vars:
        logger.error(f"[{locale_code}] Extra placeholders at {path}: {', '.join(extra_vars)}")
        PROBLEMS += 1

    missing_tags = source_tags - locale_tags
    extra_tags = locale_tags - source_tags

    if missing_tags:
        logger.error(f"[{locale_code}] Missing tags at {path}: {', '.join(missing_tags)}")
        PROBLEMS += 1

    if extra_tags:
        logger.error(f"[{locale_code}] Extra tags at {path}: {', '.join(extra_tags)}")
        PROBLEMS += 1


# ruff: noqa: C901
def _lint_formatted(locale_code: str, locale_data: str, source_data: str, path: str):
    """Validate formatted placeholders (Python only)."""
    global PROBLEMS

    def extract_fields(text: str) -> set:
        fields = set()
        for match in PLACEHOLDER_REGEX.finditer(text):
            groups = match.groupdict()
            if groups.get("py_escape"):
                continue

            if groups.get("python"):
                key = groups.get("python_key")
                fields.add(f"py:{key}" if key else "py:sequential")

        return fields

    source_fields = extract_fields(source_data)
    locale_fields = extract_fields(locale_data)

    missing = source_fields - locale_fields
    extra = locale_fields - source_fields

    def format_field_name(f):
        if f.startswith("py:"):
            return f[3:] or "{}"
        return f

    if missing:
        logger.error(
            f"[{locale_code}] Missing format fields at {path}: {', '.join(sorted(map(format_field_name, missing)))}"
        )
        PROBLEMS += 1
    if extra:
        logger.error(
            f"[{locale_code}] Extra format fields at {path}: {', '.join(sorted(map(format_field_name, extra)))}"
        )
        PROBLEMS += 1


def lint_dict(locale_code: str, locale_data: dict, source_data: dict, path: str = "", icumf: Optional[ICUMF] = None):
    """
    Recursively lint a locale dictionary against the source dictionary.

    Checking for missing keys, type mismatches, and placeholder consistency.
    """
    global PROBLEMS
    for key, source_value in source_data.items():
        current_path = f"{path}.{key}" if path else key
        if key not in locale_data:
            logger.error(f"[{locale_code}] Missing key: {current_path}")
            PROBLEMS += 1
            continue

        locale_value = locale_data[key]
        _lint(locale_code, locale_value, source_value, current_path, icumf)

    for key in locale_data.keys():
        if key not in source_data:
            current_path = f"{path}.{key}" if path else key
            logger.warning(f"[{locale_code}] Extra key: {current_path}")

    return PROBLEMS


def _lint_list(locale_code: str, locale_list: list, source_list: list, path: str, icumf: Optional[ICUMF] = None):
    global PROBLEMS
    if len(locale_list) != len(source_list):
        logger.error(
            f"[{locale_code}] List length mismatch at {path}: expected {len(source_list)}, got {len(locale_list)}"
        )
        PROBLEMS += 1
        min_length = min(len(locale_list), len(source_list))
        for i in range(min_length):
            _lint(locale_code, locale_list[i], source_list[i], f"{path}[{i}]", icumf)
    else:
        for i in range(len(source_list)):
            _lint(locale_code, locale_list[i], source_list[i], f"{path}[{i}]", icumf)
