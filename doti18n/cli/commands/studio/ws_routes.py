import json
import logging
from typing import Any, Dict

from microdot.microdot import Request
from microdot.websocket import with_websocket

from .auth import login_required
from .events import EventContext, dispatch_event
from .server import app
from .state import state

clients: Dict[Any, Dict[str, Any]] = {}


@app.route("/ws")
@with_websocket
@login_required
# ruff: noqa: C901
async def ws(request: Request, websocket):
    """WebSocket endpoint for real-time communication with the doti18n studio frontend."""
    token = request.cookies.get("session")
    from .auth import get_session

    if not token:
        return

    username = get_session(token, request.client_addr[0])
    if not username:
        return

    clients[websocket] = {"username": username, "editing": None}

    for ws_client, info in clients.items():
        editing = info.get("editing")
        if ws_client is not websocket and editing and isinstance(editing, dict):
            try:
                await websocket.send(
                    json.dumps(
                        {
                            "action": "locked",
                            "locale": editing["locale"],
                            "key": editing["key"],
                            "username": info["username"],
                        }
                    )
                )
            except Exception:
                pass

    try:
        while True:
            data = await websocket.receive()
            if not data:
                break

            try:
                message = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                logging.warning(f"Invalid JSON from user '{username}': {data!r}")
                continue

            action = message.get("action")
            if not isinstance(action, str):
                continue

            context = EventContext(username=username, clients=clients, state=state)
            await dispatch_event(action, websocket, message, context)

    finally:
        # Release all server-side locks for this user
        if state is not None:
            released = state.release_all_locks(username)
            for locale, key in released:
                logging.info(f"User '{username}' disconnected, releasing lock on '{locale}': {key}")
                unlock_msg = json.dumps({"action": "unlocked", "locale": locale, "key": key, "username": username})
                for client in clients:
                    if client is not websocket:
                        try:
                            await client.send(unlock_msg)
                        except Exception:
                            pass

        del clients[websocket]
