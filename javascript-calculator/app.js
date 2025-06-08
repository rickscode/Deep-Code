// app.js
const inputField = document.getElementById('input-field');
const clearBtn = document.getElementById('clear-btn');
const backspaceBtn = document.getElementById('backspace-btn');
const numberBtns = document.querySelectorAll('.number-btn');
const operationBtns = document.querySelectorAll('.operator-btn');
const equalsBtn = document.getElementById('equals-btn');

let currentOperation = '';
let currentNumber = '';

clearBtn.addEventListener('click', () => {
    inputField.value = '';
    currentOperation = '';
    currentNumber = '';
});

backspaceBtn.addEventListener('click', () => {
    inputField.value = inputField.value.length > 0 ? inputField.value.slice(0, -1) : '';
});

numberBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
        inputField.value += btn.textContent;
        currentNumber += btn.textContent;
    });
});

operationBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
        if (currentOperation !== '') {
            inputField.value += ' ' + currentOperation + ' ';
            currentNumber = '';
        }
        currentOperation = btn.textContent;
    });
});

equalsBtn.addEventListener('click', () => {
    if (currentOperation !== '') {
        inputField.value = eval(inputField.value);
        currentOperation = '';
        currentNumber = '';
    }
});
