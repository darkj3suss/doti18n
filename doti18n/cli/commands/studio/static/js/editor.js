import { translations, activeKey, currentLocale, lockedKeys, getSocket } from './state.js';
import { updateTranslationCache } from './utils.js';
import { showStatus } from './status.js';
import { updateStatusDotsForHierarchy } from './tree.js'; 
import { applyFilters } from './filters.js';

const textarea = document.getElementById('editor-textarea');

let draggingMacro = null;
let _sendUpdateTimeout = null;

export function initEditor() {
    textarea.onfocus = () => {
        const socket = getSocket();
        if (!activeKey || !socket || socket.readyState !== WebSocket.OPEN) return;
        socket.send(JSON.stringify({ action: 'start_edit', locale: currentLocale, key: activeKey }));
    };

    textarea.onblur = () => {
        const socket = getSocket();
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
                // trigger input event manually
                const event = new Event('input', {bubbles: true});
                textarea.dispatchEvent(event);
            }
        }
    });

    textarea.onkeydown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            textarea.blur();
        }
    };
}

export function setEditorContent(text) {
    const macroRegex = /@([a-zA-Z0-9_-]+)/g;
    const html = text.replace(macroRegex, (match, name) => {
        return `<span class="macro" contenteditable="false" data-name="${name}" draggable="true" title="Click to expand">@${name}</span>`;
    });
    textarea.innerHTML = html;
    initMacroEvents();
}

export function getEditorContent() {
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

function getMacroValue(name) {
    const macroSources = ['__macros__', '__doti18n__'];
    for (const source of macroSources) {
        if (translations[source] && translations[source][name]) {
            return translations[source][name];
        }
    }
    return null;
}

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

function sendUpdate(key, value) {
    if (_sendUpdateTimeout) {
        clearTimeout(_sendUpdateTimeout);
    }
    _sendUpdateTimeout = setTimeout(() => {
        _sendUpdateTimeout = null;
        _flushUpdate(key, value);
    }, 5000);
}

function _flushUpdate(key, value) {
    const socket = getSocket();
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

export function flushPendingUpdate() {
    if (_sendUpdateTimeout && activeKey) {
        clearTimeout(_sendUpdateTimeout);
        _sendUpdateTimeout = null;
        const value = getEditorContent();
        _flushUpdate(activeKey, value);
    }
}

