import json
import logging

from . import EventContext, register_event

logger = logging.getLogger("doti18n.studio")


@register_event("update")
async def handle_update(websocket, message, context: EventContext):
    """Handle the 'update' event when a user updates a translation key."""
    locale = message.get("locale")
    key_path = message.get("key")
    value = message.get("value")

    if not locale or not key_path:
        await websocket.send(json.dumps({"action": "error", "message": "Missing locale or key"}))
        return

    if not isinstance(value, str):
        await websocket.send(json.dumps({"action": "error", "message": "Value must be a string"}))
        return

    if locale not in context.state.get_locales():
        await websocket.send(json.dumps({"action": "error", "message": f"Locale '{locale}' not found"}))
        return

    lock_owner = context.state.get_lock_owner(locale, key_path)
    if lock_owner and lock_owner != context.username:
        await websocket.send(json.dumps({"action": "error", "message": f"Key '{key_path}' is locked by {lock_owner}"}))
        return

    logger.info(f"User '{context.username}' updated translation '{locale}': {key_path} = {value}")
    context.state.update_translation(locale, key_path, value)
    update_msg = json.dumps(
        {"action": "updated", "locale": locale, "key": key_path, "value": value, "sender": context.username}
    )

    for client in context.clients:
        if client is not websocket:
            try:
                await client.send(update_msg)
            except Exception:
                pass
