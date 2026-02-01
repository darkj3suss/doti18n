import logging
import sys
from pathlib import Path

import doti18n
from doti18n import LocaleData
from doti18n.loaders import Loader

from .generate_code import generate_code

logger = logging.getLogger("doti18n.stub")


def register(subparsers):
    """Register the 'stub' command to generate stubs."""
    parser = subparsers.add_parser("stub", help="Generate stubs")
    parser.add_argument(
        "path",
        help="Path to locale's directory",
        nargs="?",
    )
    parser.add_argument("-l", "--locale", dest="default_locale", default="en", help="Default locale code (default: en)")
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

        exit(0)

    if not args.path:
        logger.error("No locale's path is provided. Use --help for more information.")
        exit(1)

    path = Path(args.path)
    if not _is_venv():
        logger.warning(
            "You are running this command outside a virtual environment.\n"
            "It`s highly not recommended to do this.\n"
            "Use a virtual environment to avoid dependency issues.\n"
        )
        inp = input("Do you want to continue? (y/N)\n>>> ")
        if inp.lower() != "y":
            print("Aborting...")
            exit(0)

    i18n = LocaleData(path, args.default_locale, strict=True, loader=Loader(strict=True, icumf=False))
    data = i18n._raw_translations
    stub_code = generate_code(data, args.default_locale)
    target_path = package_path / "__init__.pyi"
    try:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(stub_code)
    except PermissionError:
        logger.error(f"Permission denied when trying to write to '{target_path}'.")
        exit(1)

    logger.info("Stubs generated successfully!")
