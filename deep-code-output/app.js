// calculator-app/app.js
document.addEventListener('DOMContentLoaded', function() {
 const display = document.getElementById('display');
 const clearButton = document.getElementById('clear');
 const backspaceButton = document.getElementById('backspace');
 const equalsButton = document.getElementById('equals');
 const numberButtons = document.querySelectorAll('#zero, #one, #two, #three, #four, #five, #six, #seven, #eight, #nine');
 const operatorButtons = document.querySelectorAll('#add, #subtract, #multiply, #divide');
 const decimalButton = document.getElementById('decimal');

 let currentNumber = '';
 let previousNumber = '';
 let currentOperator = '';

 numberButtons.forEach(button => {
 button.addEventListener('click', function() {
 const number = button.textContent;
 currentNumber += number;
 display.value = currentNumber;
 });
 });

 operatorButtons.forEach(button => {
 button.addEventListener('click', function() {
 if (currentNumber !== '') {
 if (previousNumber !== '') {
 calculate();
 }
 previousNumber = currentNumber;
 currentNumber = '';
 currentOperator = button.textContent;
 }
 });
 });

 equalsButton.addEventListener('click', function() {
 if (currentNumber !== '' && previousNumber !== '') {
 calculate();
 previousNumber = '';
 currentOperator = '';
 }
 });

 clearButton.addEventListener('click', function() {
 currentNumber = '';
 previousNumber = '';
 currentOperator = '';
 display.value = '';
 });

 backspaceButton.addEventListener('click', function() {
 currentNumber = currentNumber.slice(0, -1);
 display.value = currentNumber;
 });

 decimalButton.addEventListener('click', function() {
 if (!currentNumber.includes('.')) {
 currentNumber += '.';
 display.value = currentNumber;
 }
 });

 function calculate() {
 const num1 = parseFloat(previousNumber);
 const num2 = parseFloat(currentNumber);
 let result;

 switch (currentOperator) {
 case '+':
 result = num1 + num2;
 break;
 case '-':
 result = num1 - num2;
 break;
 case '*':
 result = num1 * num2;
 break;
 case '/':
 if (num2 !== 0) {
 result = num1 / num2;
 } else {
 result = 'Error';
 }
 break;
 default:
 result = 0;
 }

 display.value = result;
 currentNumber = result.toString();
 }
});

calculator-app
