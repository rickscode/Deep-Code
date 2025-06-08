const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');
const todos = JSON.parse(localStorage.getItem('todos')) || [];

todoInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addTodo(todoInput.value);
        todoInput.value = '';
    }
});

function addTodo(todo) {
    const todoItem = {
        text: todo,
        completed: false
    };
    todos.push(todoItem);
    localStorage.setItem('todos', JSON.stringify(todos));
    renderTodoList();
}

function renderTodoList() {
    todoList.innerHTML = '';
    todos.forEach((todo) => {
        const todoElement = document.createElement('li');
        todoElement.textContent = todo.text;
        if (todo.completed) {
            todoElement.classList.add('completed');
        }
        todoElement.addEventListener('click', () => {
            todo.completed = !todo.completed;
            localStorage.setItem('todos', JSON.stringify(todos));
            renderTodoList();
        });
        todoList.appendChild(todoElement);
    });
}

renderTodoList();
