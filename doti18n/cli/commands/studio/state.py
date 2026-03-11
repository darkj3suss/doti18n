import logging
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from doti18n.loaders import Loader
from doti18n.utils import _deep_merge

SAVE_DEBOUNCE_SECONDS = 2


class StudioState:
    """Class to manage the state of the studio command, including loaded locales, file paths, and locks."""

    def __init__(self, path: str = ".", default_locale: str = "en"):
        """Initialize the state for the studio command."""
        self.path = Path(path)
        self.default_locale = default_locale
        self.loaders = Loader().loaders
        self.supported_extensions = self.loaders.keys()
        self.locales: Dict[str, Dict[str, Any]] = {}
        self.files: Dict[str, Path] = {}
        self.locks: Dict[str, threading.Lock] = {}
        self.global_lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Server-side key lock tracking: {(locale, key): username}
        self.active_locks: Dict[tuple, str] = {}
        self._active_locks_lock = threading.Lock()

        # Debounced save
        self._save_timer: Optional[threading.Timer] = None
        self._save_timer_lock = threading.Lock()
        self._dirty_locales: set = set()

        self.load()

    # ruff: noqa: C901
    def load(self):
        """Load all locale files from the specified directory."""
        with self.global_lock:
            if not self.path.exists():
                raise FileNotFoundError(f"Locale directory '{self.path}' does not exist.")

            if not self.path.is_dir():
                raise NotADirectoryError(f"Locale path '{self.path}' is not a directory.")

            for extension in self.supported_extensions:
                for file in self.path.glob(f"*{extension}"):
                    try:
                        if not any(file.name.endswith(ext) for ext in self.supported_extensions):
                            self.logger.warning(f"Skipping unsupported file '{file}'")
                            continue

                        loader = self.loaders.get(file.suffix)
                        if not loader:
                            self.logger.warning(f"No loader found for file '{file}' with extension '{file.suffix}'")
                            continue

                        data = loader.load_with_comments(file)
                        if isinstance(data, list):
                            self.logger.error(
                                f"File '{file}' contains multiple locales, which not supported in the studio."
                            )
                            continue

                        if not isinstance(data, dict):
                            self.logger.error(
                                f"File '{file}' has invalid format: expected a dict, got {type(data).__name__}"
                            )
                            continue

                        locale_code = file.stem.lower()
                        if locale_code in self.locales:
                            self.logger.warning(
                                f"Locale '{locale_code}' already loaded. "
                                f"File '{file}' will merge/overwrite existing keys."
                            )

                        _deep_merge(data, self.locales)
                        self.files[locale_code] = file.absolute()
                    except Exception as e:
                        self.logger.warning(f"Failed to load '{file}': {e}")

            for locale in self.locales:
                if locale not in self.locks:
                    self.locks[locale] = threading.Lock()

    def get_translation(self, locale: str) -> Optional[Dict[str, Any]]:
        """Get the translation data for a given locale."""
        return self.locales.get(locale)

    def update_translation(self, locale: str, key_path: str, value: Any):
        """Update a translation value for a given locale and key path. Key path is dot-separated for nested keys."""
        if locale not in self.locales:
            self.logger.error(f"Locale '{locale}' does not exist. Cannot update translation.")
            return

        with self.locks[locale]:
            keys = key_path.split(".")
            current = self.locales[locale]
            for key in keys[:-1]:
                if isinstance(current, list):
                    try:
                        idx = int(key)
                    except (ValueError, TypeError):
                        self.logger.error(f"Cannot index list with non-integer key '{key}' in path '{key_path}'")
                        return
                    if 0 <= idx < len(current):
                        current = current[idx]
                    else:
                        self.logger.error(f"List index {idx} out of range in path '{key_path}'")
                        return
                elif isinstance(current, dict):
                    if key not in current or not isinstance(current[key], (dict, list)):
                        current[key] = {}
                    current = current[key]
                else:
                    self.logger.error(
                        f"Cannot traverse into {type(current).__name__} with key '{key}' in path '{key_path}'"
                    )
                    return

            # Set the final value
            last_key = keys[-1]
            if isinstance(current, list):
                try:
                    idx = int(last_key)
                except (ValueError, TypeError):
                    self.logger.error(f"Cannot index list with non-integer key '{last_key}' in path '{key_path}'")
                    return
                if 0 <= idx < len(current):
                    current[idx] = value
                else:
                    self.logger.error(f"List index {idx} out of range in path '{key_path}'")
                    return
            else:
                current[last_key] = value

        self._dirty_locales.add(locale)
        self._schedule_save()

    def get_locales(self) -> list[str]:
        """Get a list of available locale codes."""
        return list(self.locales.keys())

    def acquire_key_lock(self, locale: str, key: str, username: str) -> bool:
        """Try to lock a key for editing. Returns True if acquired, False if already locked by another user."""
        with self._active_locks_lock:
            lock_key = (locale, key)
            current_owner = self.active_locks.get(lock_key)
            if current_owner and current_owner != username:
                return False
            self.active_locks[lock_key] = username
            return True

    def release_key_lock(self, locale: str, key: str, username: str) -> bool:
        """Release a key lock. Returns True if released, False if not owned."""
        with self._active_locks_lock:
            lock_key = (locale, key)
            current_owner = self.active_locks.get(lock_key)
            if current_owner == username:
                del self.active_locks[lock_key]
                return True
            return False

    def release_all_locks(self, username: str) -> list:
        """Release all locks held by a user. Returns list of (locale, key) tuples released."""
        released = []
        with self._active_locks_lock:
            to_remove = [k for k, v in self.active_locks.items() if v == username]
            for k in to_remove:
                del self.active_locks[k]
                released.append(k)
        return released

    def get_lock_owner(self, locale: str, key: str) -> Optional[str]:
        """Get the username that holds the lock, or None."""
        with self._active_locks_lock:
            return self.active_locks.get((locale, key))

    # --- Debounced save ---

    def _schedule_save(self):
        """Schedule a debounced save. Resets the timer on each call."""
        with self._save_timer_lock:
            if self._save_timer is not None:
                self._save_timer.cancel()
            self._save_timer = threading.Timer(SAVE_DEBOUNCE_SECONDS, self._debounced_save)
            self._save_timer.daemon = True
            self._save_timer.start()

    def _debounced_save(self):
        """Perform the actual save (called by timer)."""
        self.save()

    def save(self):
        """Save all locales back to their files. Cancels any pending debounced save."""
        with self._save_timer_lock:
            if self._save_timer is not None:
                self._save_timer.cancel()
                self._save_timer = None

        with self.global_lock:
            for locale, data in self.locales.items():
                if locale not in self.files:
                    self.logger.warning(f"No file path for locale '{locale}', skipping save.")
                    continue

                filename = self.files[locale]
                loader = self.loaders.get(filename.suffix)
                if not loader:
                    self.logger.error(f"No loader found for file '{filename}' with extension '{filename.suffix}'")
                    continue

                try:
                    loader.save(filename, data)
                except Exception as e:
                    self.logger.error(f"Failed to save '{filename}': {e}")

            self._dirty_locales.clear()


state: Optional[StudioState] = None


def init_state(path: str, default_locale: str = "en"):
    """Initialize the global state for the studio."""
    global state
    state = StudioState(path, default_locale)
    return state
