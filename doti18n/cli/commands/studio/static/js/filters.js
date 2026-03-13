import { translations } from './state.js';
import { getKeyValue, forEachParentNode } from './utils.js';

export function applyFilters() {
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
            forEachParentNode(file, (current) => {
                current.style.display = '';

                const folderLabel = current.querySelector(':scope > .tree-folder');
                const childrenDiv = current.querySelector(':scope > .tree-children');
                if (folderLabel && childrenDiv) {
                    if (query) {
                        folderLabel.classList.add('open');
                        childrenDiv.classList.add('open');
                    }
                }
            }, true);
        }
    });
}
