import { activeKey, lockedKeys } from './state.js';

let statusInterval = null;

export function showStatus(msg, persistent = false) {
    const status = document.getElementById('save-status');
    if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
    }

    if (msg.endsWith('...')) {
        const baseMsg = msg.slice(0, -3);
        let dots = 3;
        status.textContent = baseMsg + '...';
        statusInterval = setInterval(() => {
            dots = (dots % 3) + 1;
            status.textContent = baseMsg + '.'.repeat(dots);
        }, 500);
    } else {
        status.textContent = msg;
    }

    if (!persistent) {
        setTimeout(() => {
            const currentStatus = status.textContent;
            const baseMsg = msg.endsWith('...') ? msg.slice(0, -3) : msg;

            if (currentStatus.startsWith(baseMsg)) {
                if (activeKey && lockedKeys[activeKey]) {
                    showStatus(`${lockedKeys[activeKey]} is editing this key...`, true);
                } else {
                    showStatus('Ready');
                }
            }
        }, 3000);
    }
}

