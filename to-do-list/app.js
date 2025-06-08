const newTodoInput = document.getElementById('new-todo');
const todoList = document.getElementById('todo-list');

let todoItems = [];

newTodoInput.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
        addTodoItem(newTodoInput.value));
        newTodoInput.value = '';
    }
});

function addTodoItem(todoItem) {
    todoItems.push({ text: todoItem(todoItem) });
    renderTodoList();
}

function renderTodoList() {
    todoList.innerHTML = '';
    todoItems.forEach((todoItem) => {
        const todoListItem = document.createElement('li');
        todoListItem.textContent = todoItem.text;
        todoList.appendChild(todoListItem);
    });
