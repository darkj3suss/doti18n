import { findLabelByKey, forEachParentNode } from './utils.js';
import { activeKey, getSocket, lockedKeys } from './state.js';
import { showStatus } from './status.js';

export function updateLockUI(key, username) {
    const el = findLabelByKey(key);
    if (!el) return;

    if (username) {
        el.classList.add('locked');
        el.setAttribute('title', `${username} is editing...`);
        let badge = el.querySelector('.lock-badge');
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'lock-badge';
            el.appendChild(badge);
        }
        badge.textContent = `${username} editing...`;
    } else {
        el.classList.remove('locked');
        el.removeAttribute('title');
        const badge = el.querySelector('.lock-badge');
        if (badge) badge.remove();
    }

    updateParentLockStatus(el);
    
    // Also check if valid activeKey
    if (activeKey === key) {
        updateEditorLockState(key);
    }
}

export function updateEditorLockState(key) {
    const textarea = document.getElementById('editor-textarea');
    const socket = getSocket();
    const username = lockedKeys[key];
    
    if (username || !socket || socket.readyState !== WebSocket.OPEN) {
        textarea.setAttribute('contenteditable', 'false');
        textarea.classList.add('locked-editor');
        if (username) {
            showStatus(`${username} is editing this key...`, true);
        } else {
            showStatus('Disconnected from server', true);
        }
    } else {
        textarea.setAttribute('contenteditable', 'true');
        textarea.classList.remove('locked-editor');
        showStatus('Ready');
    }
}

export function updateParentLockStatus(label) {
    forEachParentNode(label, (parentNode) => {
        const parentLabel = parentNode.querySelector(':scope > .tree-label.tree-folder');
        const childrenDiv = parentNode.querySelector(':scope > .tree-children');

        if (parentLabel && childrenDiv) {
            const lockedChildren = Array.from(childrenDiv.querySelectorAll('.tree-label.locked'));
            const isCollapsed = !childrenDiv.classList.contains('open');

            let badge = parentLabel.querySelector('.parent-lock-badge');
            if (lockedChildren.length > 0 && isCollapsed) {
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'parent-lock-badge';
                    parentLabel.appendChild(badge);
                }
                const firstLocked = lockedChildren[0];
                const lockBadge = firstLocked ? firstLocked.querySelector('.lock-badge') : null;
                const username = lockBadge ? lockBadge.textContent.replace(' editing...', '') : '';
                badge.textContent = username ? `${username} editing...` : 'Editing...';
            } else {
                if (badge) badge.remove();
            }
        }
    }, false);
}
