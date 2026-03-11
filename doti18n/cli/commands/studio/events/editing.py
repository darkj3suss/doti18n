import json
import logging

from . import EventContext, register_event

logger = logging.getLogger("doti18n.studio")


@register_event("start_edit")
async def handle_start_edit(websocket, message, context: EventContext):
    """Handle the 'start_edit' event when a user starts editing a translation key."""
    locale = message.get("locale")
    key_path = message.get("key")

    if not locale or not key_path:
        await websocket.send(json.dumps({"action": "error", "message": "Missing locale or key"}))
        return

    if not context.state.acquire_key_lock(locale, key_path, context.username):
        owner = context.state.get_lock_owner(locale, key_path)
        await websocket.send(
            json.dumps({"action": "error", "message": f"Key '{key_path}' is already being edited by {owner}"})
        )
        return

    context.clients[websocket]["editing"] = {"locale": locale, "key": key_path}
    logger.debug(f"User '{context.username}' started editing '{locale}': {key_path}")

    lock_msg = json.dumps({"action": "locked", "locale": locale, "key": key_path, "username": context.username})
    for client in context.clients:
        if client is not websocket:
            try:
                await client.send(lock_msg)
            except Exception:
                pass


@register_event("stop_edit")
async def handle_stop_edit(websocket, _message, context: EventContext):
    """Handle the 'stop_edit' event when a user stops editing a translation key."""
    editing = context.clients[websocket]["editing"]
    if editing:
        locale = editing["locale"]
        key_path = editing["key"]
        context.state.release_key_lock(locale, key_path, context.username)
        logger.debug(f"User '{context.username}' stopped editing '{locale}': {key_path}")
        unlock_msg = json.dumps({"action": "unlocked", "locale": locale, "key": key_path, "username": context.username})
        context.clients[websocket]["editing"] = None
        for client in context.clients:
            if client is not websocket:
                try:
                    await client.send(unlock_msg)
                except Exception:
                    pass
