const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');
const todos = [];

todoInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addTodo(todoInput.value);
        todoInput.value = '';
    }
});

function addTodo(todo) {
    const todoItem = document.createElement('li');
    todoItem.textContent = todo;
    todoList.appendChild(todoItem);
    todos.push(todo);
}

// Add some sample todos
addTodo('Buy milk');
addTodo('Walk the dog');
