const API_URL = "http://localhost:3000";
const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "login.html";
}

const listContainer = document.getElementById("list-container");
const titleBox = document.getElementById("title-box");
const inputBox = document.getElementById("input-box");
const dateInput = document.getElementById("date-input");

let editingTaskId = null;

loadTodos();

function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}

async function loadTodos() {
    const res = await fetch(`${API_URL}/user/todos`, {
        headers: { "Authorization": "Bearer " + token }
    });

    const todos = await res.json();
    
    listContainer.innerHTML = "";

    if (todos.length === 0) {
        listContainer.innerHTML = "<li>Aucune tâche pour le moment</li>";
    } else {
        todos.forEach(todo => createTaskElement(todo));
    }
}

function createTaskElement(todo) {
    const li = document.createElement("li");
    
    if (todo.status === "done") {
        li.className = "completed";
    }
    
    li.innerHTML = `
        <div class="task-content">
            <div class="task-title">${todo.title}</div>
            <div class="task-description">${todo.description}</div>
            <div class="task-date">${formatDate(todo.due_time)}</div>
        </div>
        <div class="task-actions">
            <button onclick="toggleTask(${todo.id}, '${todo.status}')">
                ${todo.status === "done" ? "↩️" : "✓"}
            </button>
            <button onclick="openEditModal(${todo.id})">✏️</button>
            <button onclick="deleteTodo(${todo.id})">❌</button>
        </div>
    `;
    
    listContainer.appendChild(li);
}

async function addTask() {
    const title = titleBox.value.trim();
    const description = inputBox.value.trim();
    const dueTime = dateInput.value;

    if (!title || !description || !dueTime) {
        alert("Veuillez remplir tous les champs");
        return;
    }

    await fetch(`${API_URL}/todos`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            title: title,
            description: description,
            due_time: dueTime,
            status: "todo"
        })
    });

    titleBox.value = "";
    inputBox.value = "";
    dateInput.value = "";

    loadTodos();
}

async function deleteTodo(id) {
    if (!confirm("Voulez-vous vraiment supprimer cette tâche ?")) {
        return;
    }

    await fetch(`${API_URL}/todos/${id}`, {
        method: "DELETE",
        headers: { "Authorization": "Bearer " + token }
    });

    loadTodos();
}

async function toggleTask(id, currentStatus) {
    const newStatus = currentStatus === "done" ? "todo" : "done";
    
    await fetch(`${API_URL}/todos/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ status: newStatus })
    });

    loadTodos();
}

async function openEditModal(id) {
    const res = await fetch(`${API_URL}/todos/${id}`, {
        headers: { "Authorization": "Bearer " + token }
    });
    const todo = await res.json();
    
    document.getElementById("edit-title").value = todo.title;
    document.getElementById("edit-description").value = todo.description;
    document.getElementById("edit-date").value = todo.due_time;
    
    editingTaskId = id;
    
    document.getElementById("edit-modal").style.display = "flex";
}

function closeModal() {
    document.getElementById("edit-modal").style.display = "none";
    editingTaskId = null;
}

async function saveEdit() {
    const title = document.getElementById("edit-title").value.trim();
    const description = document.getElementById("edit-description").value.trim();
    const dueTime = document.getElementById("edit-date").value;

    if (!title || !description || !dueTime) {
        alert("Tous les champs sont obligatoires");
        return;
    }

    await fetch(`${API_URL}/todos/${editingTaskId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            title: title,
            description: description,
            due_time: dueTime
        })
    });

    closeModal();
    
    loadTodos();
}

function formatDate(dateString) {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}