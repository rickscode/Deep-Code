const taskList = document.getElementById('task-list');
const newTaskInput = document.getElementById('new-task');

newTaskInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const task = newTaskInput.value.trim();
        if (task) {
            addTask(task);
            newTaskInput.value = '';
        }
    }
});

function addTask(task) {
    const taskElement = document.createElement('li');
    taskElement.textContent = task;
    taskList.appendChild(taskElement);
}

function loadTasks() {
    // TO DO: load tasks from local storage or API
}

loadTasks();
