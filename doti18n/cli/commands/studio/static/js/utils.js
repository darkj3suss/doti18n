import { keyElementMap, translations } from './state.js';

export function debounce(func, wait) {
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

export function findLabelByKey(key) {
    return keyElementMap.get(key);
}

export function getKeyValue(obj, keyPath) {
    const parts = keyPath.split('.');
    let current = obj;
    for (const part of parts) {
        if (current === undefined || current === null) return undefined;
        current = current[part];
    }
    return current;
}

export function forEachParentNode(element, callback, includeSelf = false) {
    let current = element.closest('.tree-node');
    if (!includeSelf && current) {
         current = current.parentElement ? current.parentElement.closest('.tree-node') : null;
    }
    
    while (current && current.id !== 'keys-tree') {
        callback(current);
        if (!current.parentElement) break;
        current = current.parentElement.closest('.tree-node');
    }
}

export function isPlainObject(val) {
    return typeof val === 'object' && val !== null && !Array.isArray(val);
}

export function updateTranslationCache(key, value) {
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
