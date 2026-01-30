import argparse
import logging
import sys

import colorlog

from .commands.generate_stub import command as stub_cmd


def setup_logging():
    """Set up colorized logging for the CLI."""
    colorlog.basicConfig(
        level=logging.INFO,
        format="%(log_color)s[%(levelname)s]%(reset)s %(name)s: %(cyan)s%(message)s",
        log_colors={
            "DEBUG": "bold_cyan",
            "INFO": "bold_green",
            "WARNING": "bold_yellow",
            "ERROR": "bold_red",
            "CRITICAL": "bold_red,bg_white",
        },
    )


def main():
    """Entry point for the doti18n CLI."""
    parser = argparse.ArgumentParser(prog="doti18n")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    stub_cmd.register(subparsers)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    setup_logging()
    args = parser.parse_args()
    args.func(args)
