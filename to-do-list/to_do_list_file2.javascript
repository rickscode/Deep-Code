const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');

todoInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addTodo();
        }
    });

function addTodo() {
    const todoText = todoInput.value.trim();
    if (todoText) {
            const todoItem = document.createElement('li');
            todoItem.textContent = todoText;
            todoList.appendChild(todoItem);
            todoInput.value = '';
        }
    }
}
