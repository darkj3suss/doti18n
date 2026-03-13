import { currentLocale, activeKey, lockedKeys, setSocket } from './state.js';
import { updateTranslationCache } from './utils.js';
import { showStatus } from './status.js';
import { updateLockUI } from './lock.js';
import { updateStatusDotsForHierarchy, highlightKey } from './tree.js';
import { setEditorContent } from './editor.js';
import { applyFilters } from './filters.js';

export function connectWS() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws`);
    setSocket(socket);

    const textarea = document.getElementById('editor-textarea');

    socket.onopen = () => {
        console.log('WS Connected');
        showStatus('Connected');
        if (activeKey && !lockedKeys[activeKey]) {
            textarea.setAttribute('contenteditable', 'true');
        }
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.action === 'updated' && data.locale === currentLocale) {
            updateTranslationCache(data.key, data.value);

            if (activeKey === data.key) {
                if (document.activeElement === textarea) return;
                setEditorContent(data.value);
            }

            updateStatusDotsForHierarchy(data.key);
            highlightKey(data.key);
            showStatus('Updated from server');
            if (document.getElementById('untranslated-only').checked) {
                applyFilters();
            }
        } else if (data.action === 'locked' && data.locale === currentLocale) {
            lockedKeys[data.key] = data.username;
            updateLockUI(data.key, data.username);
        } else if (data.action === 'unlocked' && data.locale === currentLocale) {
            delete lockedKeys[data.key];
            updateLockUI(data.key, null);
        }
    };

    socket.onclose = () => {
        showStatus('Disconnected. Reconnecting...', true);
        textarea.setAttribute('contenteditable', 'false');
        setTimeout(connectWS, 2000);
    };
}

