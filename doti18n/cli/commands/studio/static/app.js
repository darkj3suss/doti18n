let socket;
let currentLocale;
let defaultLocale;
let translations = {};
let sourceTranslations = {};
let activeKey = null;
let lockedKeys = {};
let statusInterval = null;
const keyElementMap = new Map();

const textarea = document.getElementById('editor-textarea');

function findLabelByKey(key) {
    return keyElementMap.get(key);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function connectWS() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

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

function updateLockUI(key, username) {
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

    if (activeKey === key) {
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
}

function updateParentLockStatus(label) {
    const node = label.closest('.tree-node');
    if (!node) return;

    let current = node.parentElement;
    while (current && current.id !== 'keys-tree') {
        const parentNode = current.closest('.tree-node');
        if (parentNode) {
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
            current = parentNode.parentElement;
        } else {
            break;
        }
    }
}

function highlightKey(key) {
    let el = findLabelByKey(key);
    if (!el) return;

    let current = el.parentElement;
    let targetToHighlight = el;

    while (current && current.id !== 'keys-tree') {
        const parentNode = current.closest('.tree-node');
        if (parentNode) {
            const parentLabel = parentNode.querySelector(':scope > .tree-label.tree-folder');
            const childrenDiv = parentNode.querySelector(':scope > .tree-children');
            if (childrenDiv && !childrenDiv.classList.contains('open')) {
                targetToHighlight = parentLabel;
            }
            current = parentNode.parentElement;
        } else {
            break;
        }
    }

    targetToHighlight.classList.remove('flash-update');
    void targetToHighlight.offsetWidth;
    targetToHighlight.classList.add('flash-update');
    setTimeout(() => targetToHighlight.classList.remove('flash-update'), 2000);
}

function updateTranslationCache(key, value) {
    const parts = key.split('.');
    let current = translations;
    for (let i = 0; i < parts.length - 1; i++) {
        const part = parts[i];
        if (Array.isArray(current)) {
            const idx = parseInt(part, 10);
            if (isNaN(idx) || idx < 0 || idx >= current.length) return;
            current = current[idx];
        } else {
            if (typeof current[part] !== 'object' || current[part] === null) {
                current[part] = {};
            }
            current = current[part];
        }
    }
    const lastPart = parts[parts.length - 1];
    if (Array.isArray(current)) {
        const idx = parseInt(lastPart, 10);
        if (isNaN(idx) || idx < 0 || idx >= current.length) return;
        current[idx] = value;
    } else {
        current[lastPart] = value;
    }
}

function showStatus(msg, persistent = false) {
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

const resizer = document.getElementById('resizer');
const leftPanel = document.getElementById('left-panel');
let isResizing = false;

resizer.addEventListener('mousedown', (e) => {
    isResizing = true;
    resizer.classList.add('dragging');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    e.preventDefault();
});

window.addEventListener('mousemove', (e) => {
    if (!isResizing) return;
    const offsetLeft = e.clientX;
    if (offsetLeft > 200 && offsetLeft < window.innerWidth - 300) {
        leftPanel.style.width = `${offsetLeft}px`;
    }
});

window.addEventListener('mouseup', () => {
    if (isResizing) {
        isResizing = false;
        resizer.classList.remove('dragging');
        document.body.style.cursor = 'default';
        document.body.style.userSelect = '';
    }
});

async function loadConfig() {
    try {
        const r = await fetch('/api/config');
        if (!r.ok) throw new Error(`Config request failed: ${r.status}`);
        const config = await r.json();
        defaultLocale = config.default_locale;
        const sr = await fetch(`/api/translations/${defaultLocale}`);
        if (!sr.ok) throw new Error(`Source translations request failed: ${sr.status}`);
        sourceTranslations = await sr.json();
    } catch (e) {
        console.error('Failed to load config:', e);
        showStatus('Failed to load config', true);
    }
}

async function loadTranslations(locale) {
    currentLocale = locale;
    activeKey = null;
    document.getElementById('current-key').textContent = 'Select a key to edit';
    textarea.innerHTML = '';
    textarea.setAttribute('contenteditable', 'false');
    showStatus('Loading...');

    if (!defaultLocale) await loadConfig();

    try {
        const r = await fetch(`/api/translations/${locale}`);
        if (!r.ok) throw new Error(`Translations request failed: ${r.status}`);
        translations = await r.json();
        renderTree();
        applyFilters();
        showStatus('Ready');
    } catch (e) {
        console.error('Failed to load translations:', e);
        showStatus('Failed to load translations', true);
    }
}

function renderTree() {
    const container = document.getElementById('keys-tree');
    keyElementMap.clear();
    container.replaceChildren();
    const newContainer = container.cloneNode(false);
    container.parentNode.replaceChild(newContainer, container);
    newContainer.addEventListener('click', (e) => {
        const label = e.target.closest('.tree-label');
        if (!label) return;

        const key = label.dataset.key;
        if (label.classList.contains('tree-folder')) {
            e.stopPropagation();
            label.classList.toggle('open');
            const childrenDiv = label.parentNode.querySelector('.tree-children');
            if (childrenDiv) childrenDiv.classList.toggle('open');
            updateParentLockStatus(label);
        } else {
            e.stopPropagation();
            selectKey(key);
        }
    });

    const treeData = buildTreeData(translations);
    const fragment = document.createDocumentFragment();
    renderNodes(treeData, fragment, '');
    newContainer.appendChild(fragment);
    updateStatusDots(newContainer);
}

function buildTreeData(obj) {
    const nodes = [];
    for (const key in obj) {
        if (key.startsWith('comment_')) continue;

        if (typeof obj[key] === 'object' && obj[key] !== null) {
            nodes.push({ key, children: buildTreeData(obj[key]), type: 'folder' });
        } else {
            nodes.push({ key, value: obj[key], type: 'file' });
        }
    }
    return nodes;
}

function renderNodes(nodes, container, prefix) {
    nodes.forEach(node => {
        const fullKey = prefix ? `${prefix}.${node.key}` : node.key;
        const nodeDiv = document.createElement('div');
        nodeDiv.className = 'tree-node';

        const label = document.createElement('div');
        label.className = `tree-label ${node.type === 'folder' ? 'tree-folder' : 'tree-file'}`;

        const dot = document.createElement('span');
        dot.className = 'status-dot';
        label.appendChild(dot);

        const text = document.createElement('span');
        text.className = 'label-text';
        text.textContent = node.key;
        label.appendChild(text);
        label.dataset.key = fullKey;
        keyElementMap.set(fullKey, label);
        nodeDiv.appendChild(label);

        if (node.type === 'folder') {
            const childrenDiv = document.createElement('div');
            childrenDiv.className = 'tree-children';
            renderNodes(node.children, childrenDiv, fullKey);
            nodeDiv.appendChild(childrenDiv);
        }
        container.appendChild(nodeDiv);
    });
}

function updateStatusDots(container) {
    const labels = container.querySelectorAll(':scope > .tree-node > .tree-label');
    labels.forEach(label => {
        const key = label.dataset.key;
        const dot = label.querySelector('.status-dot');
        if (!dot) return;

        if (currentLocale === defaultLocale) {
            dot.style.display = 'none';
            dot.classList.remove('status-red');
            dot.classList.add('status-green');
            return;
        } else {
            dot.style.display = 'inline-block';
        }

        if (label.classList.contains('tree-file')) {
            const sourceValue = getKeyValue(sourceTranslations, key);
            const currentValue = getKeyValue(translations, key);

            const isTranslated = (sourceValue !== currentValue && currentValue !== "");

            dot.classList.toggle('status-red', !isTranslated);
            dot.classList.toggle('status-green', isTranslated);
        } else {
            const node = label.closest('.tree-node');
            const childrenDiv = node.querySelector(':scope > .tree-children');
            if (childrenDiv) {
                const childDots = childrenDiv.querySelectorAll('.status-dot');
                const hasUntranslated = Array.from(childDots).some(d => d.classList.contains('status-red'));
                dot.classList.toggle('status-red', hasUntranslated);
                dot.classList.toggle('status-green', !hasUntranslated);
            }
        }
    });
}

function getKeyValue(obj, keyPath) {
    const parts = keyPath.split('.');
    let current = obj;
    for (const part of parts) {
        if (current === undefined || current === null) return undefined;
        current = current[part];
    }
    return current;
}

function selectKey(key) {
    activeKey = key;
    document.querySelectorAll('.tree-label').forEach(el => el.classList.remove('active'));
    const activeEl = findLabelByKey(key);
    if (activeEl) activeEl.classList.add('active');

    const value = getKeyValue(translations, key) || '';
    document.getElementById('current-key').textContent = key;
    setEditorContent(value);

    if (lockedKeys[key] || !socket || socket.readyState !== WebSocket.OPEN) {
        textarea.setAttribute('contenteditable', 'false');
        textarea.classList.add('locked-editor');
        if (lockedKeys[key]) {
            showStatus(`${lockedKeys[key]} is editing this key...`, true);
        } else {
            showStatus('Disconnected from server', true);
        }
    } else {
        textarea.setAttribute('contenteditable', 'true');
        textarea.classList.remove('locked-editor');
        textarea.focus();
    }
}



let _sendUpdateTimeout = null;

function sendUpdate(key, value) {
    if (_sendUpdateTimeout) {
        clearTimeout(_sendUpdateTimeout);
    }
    _sendUpdateTimeout = setTimeout(() => {
        _sendUpdateTimeout = null;
        _flushUpdate(key, value);
    }, 800);
}

function _flushUpdate(key, value) {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    socket.send(JSON.stringify({
        action: 'update',
        locale: currentLocale,
        key: key,
        value: value
    }));

    updateStatusDotsForHierarchy(key);
    showStatus('Saved');
}

function flushPendingUpdate() {
    if (_sendUpdateTimeout && activeKey) {
        clearTimeout(_sendUpdateTimeout);
        _sendUpdateTimeout = null;
        const value = getEditorContent();
        _flushUpdate(activeKey, value);
    }
}


textarea.onfocus = () => {
    if (!activeKey || !socket || socket.readyState !== WebSocket.OPEN) return;
    socket.send(JSON.stringify({ action: 'start_edit', locale: currentLocale, key: activeKey }));
};

textarea.onblur = () => {
    if (!activeKey || !socket || socket.readyState !== WebSocket.OPEN) return;
    flushPendingUpdate();
    socket.send(JSON.stringify({ action: 'stop_edit' }));
};

textarea.oninput = (e) => {
    if (!activeKey) return;
    const newValue = getEditorContent();
    updateTranslationCache(activeKey, newValue);

    showStatus('Saving...');
    sendUpdate(activeKey, newValue);
    if (document.getElementById('untranslated-only').checked) {
        applyFilters();
    }
};

textarea.onpaste = (e) => {
    e.preventDefault();
    const text = (e.originalEvent || e).clipboardData.getData('text/plain');
    document.execCommand('insertText', false, text);
};

function updateStatusDotsForHierarchy(key) {
    let el = findLabelByKey(key);
    if (!el) return;

    while (el) {
        const container = el.parentElement.parentElement;
        if (container) updateStatusDots(container);

        const node = el.closest('.tree-node');
        const parentNode = node.parentElement.closest('.tree-node');
        el = parentNode ? parentNode.querySelector(':scope > .tree-label') : null;
    }
}

function getMacroValue(name) {
    const macroSources = ['__macros__', '__doti18n__'];
    for (const source of macroSources) {
        if (translations[source] && translations[source][name]) {
            return translations[source][name];
        }
    }
    return null;
}

function setEditorContent(text) {
    const macroRegex = /@([a-zA-Z0-9_-]+)/g;
    const html = text.replace(macroRegex, (match, name) => {
        return `<span class="macro" contenteditable="false" data-name="${name}" draggable="true" title="Click to expand">@${name}</span>`;
    });
    textarea.innerHTML = html;
    initMacroEvents();
}

function getEditorContent() {
    let content = "";
    textarea.childNodes.forEach(node => {
        if (node.nodeType === Node.TEXT_NODE) {
            content += node.textContent;
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.classList.contains('macro')) {
                content += `@${node.dataset.name}`;
            } else if (node.tagName === 'DIV' || node.tagName === 'P') {
                content += "\n" + node.innerText;
            } else if (node.tagName === 'BR') {
                content += "\n";
            } else {
                content += node.textContent;
            }
        }
    });
    return content.trim();
}

let draggingMacro = null;

function initMacroEvents() {
    document.querySelectorAll('.macro').forEach(macro => {
        macro.onclick = (e) => {
            e.stopPropagation();
            const name = macro.dataset.name;
            const isExpanded = macro.classList.contains('expanded');
            if (isExpanded) {
                macro.textContent = `@${name}`;
                macro.classList.remove('expanded');
            } else {
                const value = getMacroValue(name);
                if (value !== null) {
                    macro.textContent = value;
                    macro.classList.add('expanded');
                }
            }
        };

        macro.ondragstart = (e) => {
            draggingMacro = macro;
            e.dataTransfer.setData('text/plain', `@${macro.dataset.name}`);
            e.dataTransfer.effectAllowed = 'move';
            macro.classList.add('dragging');
        };

        macro.ondragend = () => {
            macro.classList.remove('dragging');
            draggingMacro = null;
        };
    });
}

textarea.addEventListener('dragover', (e) => {
    e.preventDefault();
});

textarea.addEventListener('drop', (e) => {
    e.preventDefault();
    const data = e.dataTransfer.getData('text/plain');
    if (data.startsWith('@')) {
        const name = data.substring(1);
        const range = document.caretRangeFromPoint(e.clientX, e.clientY);
        if (range) {
            const macroSpan = document.createElement('span');
            macroSpan.className = 'macro';
            macroSpan.setAttribute('contenteditable', 'false');
            macroSpan.setAttribute('data-name', name);
            macroSpan.setAttribute('draggable', 'true');
            macroSpan.setAttribute('title', 'Click to expand');
            macroSpan.textContent = `@${name}`;
            
            if (draggingMacro && draggingMacro.parentNode === textarea) {
                draggingMacro.remove();
            }
            
            range.insertNode(macroSpan);
            initMacroEvents();
            textarea.oninput();
        }
    }
});

textarea.onkeydown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        textarea.blur();
    }
};


document.getElementById('expand-all').onclick = () => {
    document.querySelectorAll('.tree-folder, .tree-children').forEach(el => el.classList.add('open'));
    document.querySelectorAll('.tree-label.tree-folder').forEach(el => {
        const badge = el.querySelector('.parent-lock-badge');
        if (badge) badge.remove();
    });
};

document.getElementById('collapse-all').onclick = () => {
    document.querySelectorAll('.tree-folder, .tree-children').forEach(el => el.classList.remove('open'));
    document.querySelectorAll('.tree-label.tree-folder').forEach(el => updateParentLockStatus(el));
};

document.getElementById('locale-selector').onchange = (e) => {
    loadTranslations(e.target.value);
};

function applyFilters() {
    const query = document.getElementById('search-keys').value.toLowerCase();
    const untranslatedOnly = document.getElementById('untranslated-only').checked;
    const allNodes = document.querySelectorAll('.tree-node');
    const allFiles = document.querySelectorAll('.tree-file');

    if (!query && !untranslatedOnly) {
        allNodes.forEach(n => n.style.display = '');
        return;
    }

    allNodes.forEach(n => n.style.display = 'none');

    allFiles.forEach(file => {
        const originalKey = file.dataset.key;
        const key = originalKey.toLowerCase();

        const value = getKeyValue(translations, originalKey);
        const valueStr = (value && typeof value === 'string') ? value.toLowerCase() : '';

        const dot = file.querySelector('.status-dot');
        const isUntranslated = dot && dot.classList.contains('status-red');

        const matchesQuery = !query || key.includes(query) || valueStr.includes(query);
        const matchesUntranslated = !untranslatedOnly || isUntranslated;

        if (matchesQuery && matchesUntranslated) {
            let current = file.closest('.tree-node');
            while (current && current.id !== 'keys-tree') {
                current.style.display = '';

                const folderLabel = current.querySelector(':scope > .tree-folder');
                const childrenDiv = current.querySelector(':scope > .tree-children');
                if (folderLabel && childrenDiv) {
                    if (query) {
                        folderLabel.classList.add('open');
                        childrenDiv.classList.add('open');
                    }
                }
                current = current.parentElement.closest('.tree-node');
            }
        }
    });
}

document.getElementById('untranslated-only').addEventListener('change', applyFilters);

document.getElementById('search-keys').addEventListener('input', debounce(applyFilters, 300));


connectWS();
loadTranslations(document.getElementById('locale-selector').value);
