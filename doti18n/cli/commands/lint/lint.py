import logging

logger = logging.getLogger("doti18n.lint")
PROBLEMS = 0


def _lint(locale_code: str, locale_data: dict, source_data: dict, path: str = ""):
    global PROBLEMS
    if isinstance(locale_data, dict) and isinstance(source_data, dict):
        lint_dict(locale_code, locale_data, source_data, path)
    elif isinstance(locale_data, list) and isinstance(source_data, list):
        _lint_list(locale_code, locale_data, source_data, path)
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


def lint_dict(locale_code: str, locale_data: dict, source_data: dict, path: str = ""):
    """Lint a locale dictionary against the source dictionary."""
    global PROBLEMS
    for key, source_value in source_data.items():
        current_path = f"{path}.{key}" if path else key
        if key not in locale_data:
            logger.error(f"[{locale_code}] Missing key: {current_path}")
            PROBLEMS += 1
            continue

        locale_value = locale_data[key]
        _lint(locale_code, locale_value, source_value, current_path)

    return PROBLEMS


def _lint_list(locale_code: str, locale_list: list, source_list: list, path: str):
    global PROBLEMS
    if len(locale_list) != len(source_list):
        logger.error(
            f"[{locale_code}] List length mismatch at {path}: expected {len(source_list)}, got {len(locale_list)}"
        )
        PROBLEMS += 1
        min_length = min(len(locale_list), len(source_list))
        for i in range(min_length):
            _lint(locale_code, locale_list[i], source_list[i], f"{path}[{i}]")
    else:
        for i in range(len(source_list)):
            _lint(locale_code, locale_list[i], source_list[i], f"{path}[{i}]")
