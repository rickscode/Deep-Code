const todoInput = document.getElementById('todo-input');
const prioritySelect = document.getElementById('priority-select');
const dueDateInput = document.getElementById('due-date-input');
const todoList = document.getElementById('todo-list');
const filterSelect = document.getElementById('filter-select');
const todos = JSON.parse(localStorage.getItem('todos')) || [];

todoInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addTodo(todoInput.value, prioritySelect.value, dueDateInput.valueAsDate);
        todoInput.value = '';
    }
});

function addTodo(todo, priority, dueDate) {
    const todoItem = {
        text: todo,
        priority: priority,
        dueDate: dueDate,
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
        if (todo.priority === 'high') {
            todoElement.classList.add('priority-high');
        } else {
            todoElement.classList.add('priority-low');
        }
        todoElement.addEventListener('click', () => {
            todo.completed = !todo.completed;
            localStorage.setItem('todos', JSON.stringify(todos));
            renderTodoList();
        });
        todoList.appendChild(todoElement);
    });
}

filterSelect.addEventListener('change', () => {
    const filterValue = filterSelect.value;
    const filteredTodos = todos.filter((todo) => {
        if (filterValue === 'all') {
            return true;
        } else if (filterValue === 'completed') {
            return todo.completed;
        } else {
            return !todo.completed;
        }
    });
    todoList.innerHTML = '';
    filteredTodos.forEach((todo) => {
        const todoElement = document.createElement('li');
        todoElement.textContent = todo.text;
        if (todo.completed') {
            todoElement.classList.add('completed');
        }
        if (todo.priority === 'high') {
            todoElement.classList.add('priority-high');
        } else {
            todoElement.classList.add('priority-low');
        }
        todoElement.addEventListener('click', () => {
            todo.completed = !todo.completed;
            localStorage.setItem('todos', JSON.stringify(todos));
            renderTodoList();
        });
        todoList.appendChild(todoElement);
    });
});

renderTodoList();
