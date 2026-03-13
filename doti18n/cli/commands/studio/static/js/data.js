import { defaultLocale, setDefaultLocale, setSourceTranslations, setCurrentLocale, setActiveKey, setTranslations } from './state.js';
import { showStatus } from './status.js';
import { renderTree } from './tree.js';
import { applyFilters } from './filters.js';

export async function loadConfig() {
    try {
        const r = await fetch('/api/config');
        if (!r.ok) throw new Error(`Config request failed: ${r.status}`);
        const config = await r.json();
        setDefaultLocale(config.default_locale);
        const sr = await fetch(`/api/translations/${config.default_locale}`);
        if (!sr.ok) throw new Error(`Source translations request failed: ${sr.status}`);
        setSourceTranslations(await sr.json());
    } catch (e) {
        console.error('Failed to load config:', e);
        showStatus('Failed to load config', true);
    }
}

export async function loadTranslations(locale) {
    setCurrentLocale(locale);
    setActiveKey(null);
    document.getElementById('current-key').textContent = 'Select a key to edit';
    const textarea = document.getElementById('editor-textarea');
    textarea.innerHTML = '';
    textarea.setAttribute('contenteditable', 'false');
    showStatus('Loading...');

    if (!defaultLocale) await loadConfig();

    try {
        const r = await fetch(`/api/translations/${locale}`);
        if (!r.ok) throw new Error(`Translations request failed: ${r.status}`);
        setTranslations(await r.json());
        renderTree();
        applyFilters();
        showStatus('Ready');
    } catch (e) {
        console.error('Failed to load translations:', e);
        showStatus('Failed to load translations', true);
    }
}

