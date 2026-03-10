import importlib
import logging
import signal
import sys

from microdot.microdot import Microdot

from .state import state

app = Microdot()
# import routes to register them with the app
importlib.import_module("doti18n.cli.commands.studio.ws_routes")
importlib.import_module("doti18n.cli.commands.studio.http_routes")


def _graceful_shutdown(reason: str = ""):
    """Shared shutdown logic."""
    if reason:
        logging.info(reason)
    if state:
        state.save()
    app.shutdown()


def shutdown_handler(sig: int, _frame):
    """Signal handler for graceful shutdown on SIGINT and SIGTERM."""
    sig_name = signal.strsignal(sig) if hasattr(signal, "strsignal") else str(sig)
    _graceful_shutdown(f"Received signal {sig_name}. Shutting down doti18n studio server...")
    sys.exit(0)


def run_server(host: str = "127.0.0.1", port: int = 5000):
    """Run the doti18n studio server."""
    signal.signal(signal.SIGINT, shutdown_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        app.run(host=host, port=port)
    except KeyboardInterrupt:
        _graceful_shutdown("Keyboard interrupt received. Shutting down doti18n studio server...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Server error: {e}")
        _graceful_shutdown()
        sys.exit(1)
