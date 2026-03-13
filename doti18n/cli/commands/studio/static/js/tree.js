import { translations, sourceTranslations, defaultLocale, currentLocale, keyElementMap, setActiveKey } from './state.js';
import { getKeyValue, findLabelByKey, forEachParentNode, isPlainObject } from './utils.js';
import { setEditorContent } from './editor.js';
import { updateParentLockStatus, updateEditorLockState } from './lock.js';

export function renderTree() {
    const container = document.getElementById('keys-tree');
    keyElementMap.clear();
    
    const newContainer = container.cloneNode(false); // Clone container without children
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

    const treeData = buildTreeData(translations, sourceTranslations);
    newContainer.innerHTML = treeData.map(node => createNodeHTML(node, '')).join('');
    newContainer.querySelectorAll('.tree-label').forEach(label => {
        keyElementMap.set(label.dataset.key, label);
    });

    updateStatusDots(newContainer);
}

function buildTreeData(target, source) {
    const nodes = [];
    const keys = new Set([...Object.keys(target || {}), ...Object.keys(source || {})]);
    const sortedKeys = Array.from(keys).sort();
    for (const key of sortedKeys) {
        if (key.startsWith('comment_')) continue;
        const targetVal = target ? target[key] : undefined;
        const sourceVal = source ? source[key] : undefined;
        const isTargetObj = isPlainObject(targetVal);
        const isSourceObj = isPlainObject(sourceVal);
        if (isTargetObj || isSourceObj) {
            nodes.push({ 
                key, 
                children: buildTreeData(isTargetObj ? targetVal : {}, isSourceObj ? sourceVal : {}), 
                type: 'folder' 
            });
        } else {
            nodes.push({ key, value: targetVal, type: 'file' });
        }
    }
    return nodes;
}

function createNodeHTML(node, prefix) {
    const fullKey = prefix ? `${prefix}.${node.key}` : node.key;
    const isFolder = node.type === 'folder';
    
    let childrenHTML = '';
    if (isFolder && node.children) {
        childrenHTML = `<div class="tree-children">${node.children.map(child => createNodeHTML(child, fullKey)).join('')}</div>`;
    }

    return `
        <div class="tree-node">
            <div class="tree-label ${isFolder ? 'tree-folder' : 'tree-file'}" data-key="${fullKey}">
                <span class="status-dot"></span>
                <span class="label-text">${node.key}</span>
            </div>
            ${childrenHTML}
        </div>
    `;
}

export function updateStatusDots(container) {
    const labels = Array.from(container.querySelectorAll('.tree-label'));
    labels.reverse().forEach(label => {
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
            const currentValue = getKeyValue(translations, key);
            const sourceValue = getKeyValue(sourceTranslations, key);
            const hasValue = (currentValue !== undefined && currentValue !== null && String(currentValue) !== "");
            let isTranslated = hasValue;

            if (hasValue && sourceValue !== undefined && sourceValue !== null) {
                if (String(currentValue) === String(sourceValue)) {
                    isTranslated = false;
                }
            }

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

export function updateStatusDotsForHierarchy(key) {
    let el = findLabelByKey(key);
    if (!el) return;

    const container = el.closest('.tree-children') || el.closest('.tree-node').parentElement;
    if (container) updateStatusDots(container);

    forEachParentNode(el, (ancestor) => {
        const label = ancestor.querySelector(':scope > .tree-label');
        const childrenDiv = ancestor.querySelector(':scope > .tree-children');
        if (label && childrenDiv) {
            const dot = label.querySelector('.status-dot');
            if (dot) {
                const childDots = childrenDiv.querySelectorAll('.status-dot');
                const hasUntranslated = Array.from(childDots).some(d => d.classList.contains('status-red'));
                dot.classList.toggle('status-red', hasUntranslated);
                dot.classList.toggle('status-green', !hasUntranslated);
                dot.style.display = (currentLocale === defaultLocale) ? 'none' : 'inline-block';
            }
        }
    }, false);
}

export function highlightKey(key) {
    let el = findLabelByKey(key);
    if (!el) return;

    let targetToHighlight = el;

    forEachParentNode(el, (parentNode) => {
        const parentLabel = parentNode.querySelector(':scope > .tree-label.tree-folder');
        const childrenDiv = parentNode.querySelector(':scope > .tree-children');
        if (childrenDiv && !childrenDiv.classList.contains('open')) {targetToHighlight = parentLabel;}
    }, false);

    targetToHighlight.classList.remove('flash-update');
    void targetToHighlight.offsetWidth;
    targetToHighlight.classList.add('flash-update');
    setTimeout(() => targetToHighlight.classList.remove('flash-update'), 2000);
}

export function selectKey(key) {
    setActiveKey(key);
    document.querySelectorAll('.tree-label').forEach(el => el.classList.remove('active'));
    const activeEl = findLabelByKey(key);
    if (activeEl) activeEl.classList.add('active');

    const value = getKeyValue(translations, key) || '';
    document.getElementById('current-key').textContent = key;
    setEditorContent(value);

    updateEditorLockState(key);
    
    const textarea = document.getElementById('editor-textarea');
    if (textarea.getAttribute('contenteditable') === 'true') {
        textarea.focus();
    }
}
