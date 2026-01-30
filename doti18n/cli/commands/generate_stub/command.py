import logging
import os
import sys
from pathlib import Path

import doti18n
from doti18n.loaders import Loader
from doti18n.utils import _deep_merge

from .generate_code import generate_code

logger = logging.getLogger("doti18n.stub")


def register(subparsers):
    """Register the 'stub' command to generate stubs."""
    parser = subparsers.add_parser("stub", help="Generate stubs")
    parser.add_argument(
        "locales_path",
        help="Path to locales directory",
        nargs="?",
    )
    parser.add_argument("-l", "--lang", dest="default_locale", default="en", help="Default locale code (default: en)")
    parser.add_argument("--clean", action="store_true", help="Remove stubs instead of generating")
    parser.set_defaults(func=handle)


def _is_venv() -> bool:
    if hasattr(sys, "real_prefix"):
        return True

    else:
        return sys.base_prefix != sys.prefix


def handle(args):
    """Handle the 'stub' command to generate or clean stubs."""
    package_path = Path(doti18n.__file__).parent.resolve()

    if args.clean:
        target_path = package_path / "__init__.pyi"
        try:
            if target_path.exists():
                target_path.unlink()
                logger.info("Stubs cleaned successfully!")
            else:
                logger.info("No stubs to clean.")
        except PermissionError:
            logger.error(f"Permission denied when trying to delete '{target_path}'.")

        return

    if not args.locales_path:
        logger.error("No locales path provided. Use --help for more information.")
        return

    locales_path = Path(args.locales_path)
    if not _is_venv():
        logger.warning(
            "You are running this command outside a virtual environment.\n"
            "It`s highly not recommended to do this.\n"
            "Use a virtual environment to avoid dependency issues.\n"
        )
        inp = input("Do you want to continue? (y/N)\n>>> ")
        if inp.lower() != "y":
            print("Aborting...")
            return

    loader = Loader(strict=True)
    data = {}
    for filename in os.listdir(locales_path):
        _deep_merge(loader.load((locales_path / filename).resolve()), data)

    stub_code = generate_code(data, args.default_locale)
    target_path = package_path / "__init__.pyi"
    try:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(stub_code)
    except PermissionError:
        logger.error(f"Permission denied when trying to write to '{target_path}'.")
        return

    logger.info("Stubs generated successfully!")
