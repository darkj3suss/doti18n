import logging
from dataclasses import dataclass
from typing import Any, Dict

logger = logging.getLogger("doti18n.studio.events")


@dataclass
class EventContext:
    """Context object passed to event handlers, containing user information, client connections, and state."""

    username: str
    clients: Dict[Any, Any]
    state: Any


_events = {}


def register_event(name):
    """Register an event handler for a specific action name."""

    def decorator(func):
        _events[name] = func
        return func

    return decorator


async def dispatch_event(action, websocket, message, context: EventContext):
    """Dispatch an event to the appropriate handler based on the action name."""
    if action in _events:
        try:
            await _events[action](websocket, message, context)
        except Exception as e:
            logger.error(f"Error handling event '{action}': {e}", exc_info=True)
    else:
        logger.error(f"Unknown event action: {action}")


# import events to register them
from . import editing as editing
from . import update_key as update_key
