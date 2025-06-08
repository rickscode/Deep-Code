const todoInput = document.getElementById('todo-input');
const addBtn = document.getElementById('add-btn');
const todoList = document.getElementById('todo-list');

let todos = [];

addBtn.addEventListener('click', addTodo);
todoList.addEventListener('click', handleTodoClick);

function addTodo() {
    const todoText = todoInput.value.trim();
    if (todoText) {
        todos.push({ text: todoText, completed: false });
        renderTodos();
        todoInput.value = '';
    }
}

function handleTodoClick(event) {
    const target = event.target;
    if (target.tagName === 'LI') {
        const todoId = target.dataset.id;
        const todo = todos.find((todo) => todo.text === target.textContent);
        if (todo) {
            todo.completed = !todo.completed;
            renderTodos();
        }
    }
}

function renderTodos() {
    todoList.innerHTML = '';
    todos.forEach((todo, index) => {
        const todoElement = document.createElement('li');
        todoElement.textContent = todo.text;
        todoElement.dataset.id = index;
        if (todo.completed) {
            todoElement.classList.add('completed');
        }
        todoList.appendChild(todoElement);
    });
}

renderTodos();
