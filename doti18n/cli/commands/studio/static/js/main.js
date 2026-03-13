import { initResizer } from './layout.js';
import { loadTranslations } from './data.js';
import { connectWS } from './socket.js';
import { initEditor } from './editor.js';
import { applyFilters } from './filters.js';
import { debounce } from './utils.js';
import { updateParentLockStatus } from './lock.js';

initResizer();
initEditor();

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

document.getElementById('untranslated-only').addEventListener('change', applyFilters);

document.getElementById('search-keys').addEventListener('input', debounce(applyFilters, 300));

connectWS();
loadTranslations(document.getElementById('locale-selector').value);

