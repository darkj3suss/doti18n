def normalize_name(name: str) -> str:
    """Convert a string to a valid Python class name by capitalizing words and removing invalid characters."""
    name = "".join(word.capitalize() for word in name.replace("-", "_").split("_") if word)
    return f"Namespace{name}"
