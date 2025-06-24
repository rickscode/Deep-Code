// script.js
const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
    '#FFEEAD', '#D4A5A5', '#C5CAE9', '#F1F1F1',
    '#2D3436', '#0984E3', '#00B894', '#55E6C1',
    '#1BCE7D', '#FF6B6B', '#4ECDC4', '#45B7D1'
];

const colorGrid = document.getElementById('colorGrid');
const hexCodeDisplay = document.getElementById('hexCode');

function createColorBoxes() {
    colors.forEach(color => {
        const box = document.createElement('div');
        box.className = 'color-box';
        box.style.backgroundColor = color;
        
        const hex = document.createElement('div');
        hex.className = 'hex-code';
        hex.textContent = color.toUpperCase();
        
        box.appendChild(hex);
        box.addEventListener('click', () => selectColor(color));
        
        colorGrid.appendChild(box);
    });
}

function selectColor(color) {
    hexCodeDisplay.textContent = color.toUpperCase();
}

function copyToClipboard() {
    const textarea = document.createElement('textarea');
    textarea.value = hexCodeDisplay.textContent;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    
    // Show feedback
    const button = document.querySelector('button');
    button.textContent = 'Copied!';
    setTimeout(() => button.textContent = 'Copy', 1000);
}

// Initialize the app
createColorBoxes();
selectColor(colors[0]); // Set initial color
