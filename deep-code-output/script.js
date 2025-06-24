document.querySelectorAll('.color-box').forEach(box => {
    box.addEventListener('click', () => {
        const hexCode = box.querySelector('.hex-code').textContent;
        navigator.clipboard.writeText(hexCode).then(() => {
            alert(`Copied ${hexCode} to clipboard!`);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    });
});
