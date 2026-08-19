function setDynamicPaddingRight(container, paddingRem = 1.5) {
    const remInPx = parseFloat(getComputedStyle(document.documentElement).fontSize); // 1rem in px
    const paddingPx = paddingRem * remInPx
    
    container.style.paddingRight = `${paddingPx}px`;

    const lastSpan = container.querySelector('li:last-child span');
    if (!lastSpan) return;

    const containerRect = container.getBoundingClientRect();
    const spanRect = lastSpan.getBoundingClientRect();

    const overflow = spanRect.right - containerRect.right;

    container.style.paddingRight = overflow > 0 
        ? `${overflow + paddingPx}px` 
        : `${paddingPx}px`;
}

const streetContainer = document.querySelector('.street-container');

window.addEventListener('load', () => setDynamicPaddingRight(streetContainer));

window.addEventListener('resize', () => setDynamicPaddingRight(streetContainer));