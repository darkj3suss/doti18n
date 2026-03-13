export let currentLocale;
export let defaultLocale;
export let translations = {};
export let sourceTranslations = {};
export let activeKey = null;
export let lockedKeys = {};
export let socket = null;
export const keyElementMap = new Map();

export function setCurrentLocale(val) { currentLocale = val; }
export function setDefaultLocale(val) { defaultLocale = val; }
export function setTranslations(val) { translations = val; }
export function setSourceTranslations(val) { sourceTranslations = val; }
export function setActiveKey(val) { activeKey = val; }
export function setSocket(val) { socket = val; }
export function getSocket() { return socket; }
