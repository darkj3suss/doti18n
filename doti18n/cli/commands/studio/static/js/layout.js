const resizer = document.getElementById('resizer');
const leftPanel = document.getElementById('left-panel');
let isResizing = false;

export function initResizer() {
    if(!resizer) return;

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
}

