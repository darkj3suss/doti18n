import logging
from pathlib import Path

from doti18n import LocaleData
from doti18n.icumf import ICUMF
from doti18n.loaders import Loader

from .lint import lint_dict

logger = logging.getLogger("doti18n.lint")


def register(subparsers):
    """Register the 'lint' command to lint translates."""
    parser = subparsers.add_parser("lint", help="Scan locales for issues")
    parser.add_argument(
        "path",
        help="Path to locale's directory",
        nargs="?",
    )
    parser.add_argument(
        "-s", "--source", dest="default_locale", default="en", help="Source of true (locale code) (default: en)"
    )
    parser.add_argument("--icumf", dest="check_icumf", action="store_true", help="Check ICU MessageFormat syntax")

    parser.set_defaults(func=handle)


def handle(args):
    """Handle the 'lint' command to lint translates."""
    if not args.path:
        logger.error("No locale's path is provided. Use --help for more information.")
        exit(1)

    path = Path(args.path)
    default_locale = args.default_locale
    icumf = ICUMF() if args.check_icumf else None
    loader = Loader(True, icumf)
    try:
        i18n = LocaleData(path, default_locale, True, loader=loader)
    except Exception as e:
        logger.error(f"Failed to load locales from path '{path}': {e}")
        exit(1)

    data = i18n._raw_translations
    source = data[default_locale]
    # files, problems
    linted = 0
    problems = 0
    for locale_code, locale_data in data.items():
        if locale_code == default_locale:
            continue

        logger.info(f"Linting locale '{locale_code}'...")
        problems += lint_dict(locale_code, locale_data, source)
        linted += 1

    if problems == 0:
        logger.info(f"Linted {linted} locales with no problems found.")
    else:
        logger.info(f"Linted {linted} locales with {problems} problems found.")
