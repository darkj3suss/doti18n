import logging
import sys

logger = logging.getLogger("doti18n.studio")


def register(subparsers):
    """Register the 'studio' command and its subcommands."""
    studio_parser = subparsers.add_parser("studio", help="doti18n studio")

    studio_subparsers = studio_parser.add_subparsers(dest="studio_command")
    run_parser = studio_subparsers.add_parser("run", help="Run the studio server")
    add_common_arguments(run_parser)
    run_parser.set_defaults(func=handle_run)
    adduser_parser = studio_subparsers.add_parser("add-user", help="Add a new user for the studio")
    adduser_parser.add_argument("username", help="Username")
    adduser_parser.add_argument("password", help="Password")
    adduser_parser.set_defaults(func=handle_add_user)
    studio_parser.set_defaults(func=lambda args: studio_parser.print_help())


def add_common_arguments(parser):
    """Add arguments for 'studio' command."""
    parser.add_argument("path", help="Path to locale's directory or file", nargs="?")
    parser.add_argument("-l", "--locale", dest="default_locale", default="en", help="Default locale code (default: en)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Port to bind (default: 5000)")


def handle_run(args):
    """Handle the 'studio run' command to invoke a web-client."""
    try:
        # noinspection PyUnusedImports
        from .state import init_state
    except ImportError:
        logger.error("Install doti18n with the 'studio' extra to use this command: pip install doti18n[studio]")
        sys.exit(1)

    if not args.path:
        logger.error("Path to locale's directory or file is required.")
        sys.exit(1)

    try:
        init_state(args.path, args.default_locale)
    except (FileNotFoundError, NotADirectoryError) as e:
        logger.error(str(e))
        sys.exit(1)

    from .server import run_server

    logger.info(f"Starting doti18n studio on http://{args.host}:{args.port}")
    run_server(args.host, args.port)


def handle_add_user(args):
    """Handle the 'studio add-user' command."""
    try:
        # noinspection PyUnusedImports
        from .auth import add_user
    except ImportError:
        logger.error("Install doti18n with the 'studio' extra to use this command: pip install doti18n[studio]")
        sys.exit(1)

    add_user(args.username, args.password)
    logging.info(f"User '{args.username}' added successfully.")


def handle(args):
    """Legacy handle function if still needed by some registry."""
    if hasattr(args, "func"):
        args.func(args)
