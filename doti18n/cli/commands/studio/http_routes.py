import os
import secrets

from microdot.microdot import Request, redirect, send_file
from tenjin import Engine  # type: ignore

# noinspection PyUnresolvedReferences
from tenjin.helpers import *  # type: ignore

from .auth import (
    clear_failed_attempts,
    create_session,
    delete_session,
    is_ip_banned,
    login_required,
    record_failed_attempt,
    verify_user,
)
from .server import app
from .state import state

template_path = os.path.join(os.path.dirname(__file__), "templates")
engine = Engine(path=[template_path])


@app.route("/")
@login_required
def index(_request: Request):
    """Render the main studio interface, passing the list of available locales to the template."""
    assert state is not None
    locales = state.get_locales()
    return engine.render("index.html", {"locales": locales}), 200, {"Content-Type": "text/html"}


@app.get("/login")
def login_form(request: Request):
    """Render the login form."""
    if is_ip_banned(request.client_addr[0]):
        return "Access denied. Your IP is temporarily banned due to too many failed login attempts.", 403

    error = request.args.get("error")
    csrf_token = secrets.token_hex(32)
    response = (
        engine.render("login.html", {"error": error, "csrf_token": csrf_token}),
        200,
        {"Content-Type": "text/html"},
    )
    return response


@app.post("/login")
def login(request: Request):
    """Process the login form submission. Verifies the user's credentials and creates a session if valid."""
    ip_address = request.client_addr[0]

    if is_ip_banned(ip_address):
        return "Access denied. Your IP is temporarily banned due to too many failed login attempts.", 403

    form = request.form
    if not form:
        record_failed_attempt(ip_address)
        return redirect("/login?error=1")

    username = form.get("username", "")
    password = form.get("password", "")

    if not username or not password:
        record_failed_attempt(ip_address)
        return redirect("/login?error=1")

    if verify_user(username, password):
        clear_failed_attempts(ip_address)

        is_localhost = request.headers.get("Host", "").split(":")[0] in ("127.0.0.1", "localhost", "::1")
        response = redirect("/")
        token = create_session(username, ip_address)
        response.set_cookie("session", token, http_only=True, secure=not is_localhost)
        return response

    record_failed_attempt(ip_address)
    return redirect("/login?error=1")


@app.route("/logout")
def logout(request: Request):
    """Log the user out by deleting their session and clearing the cookie."""
    token = request.cookies.get("session")
    if token:
        delete_session(token)
    response = redirect("/login")
    response.set_cookie("session", "", max_age=0)
    return response


@app.route("/static/<path:path>")
def static(_request: Request, path):
    """Serve static files from the 'static' directory. Caches files for 1 hour (3600 seconds) to improve performance."""
    return send_file(str(os.path.join(os.path.dirname(__file__), "static", path)), max_age=3600)


@app.get("/api/config")
@login_required
def get_config(_request: Request):
    """Get the configuration data for the studio, including available locales and default locale."""
    assert state is not None
    return {"default_locale": state.default_locale, "locales": state.get_locales()}


@app.get("/api/translations/<locale>")
@login_required
def get_translations(_request: Request, locale):
    """Get the translation data for a specific locale."""
    assert state is not None
    translations = state.get_translation(locale)
    if translations is None:
        return {"error": "Locale not found"}, 404
    return translations
