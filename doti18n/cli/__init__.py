import argparse
import logging
import sys

from .commands.generate_stub import command as stub_cmd

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s]: %(message)s",
)


def main():
    """Entry point for the doti18n CLI."""
    parser = argparse.ArgumentParser(prog="doti18n")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    stub_cmd.register(subparsers)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)
