const API_URL = "http://localhost:3000";

const token = localStorage.getItem("token");
if (token) {
    window.location.href = "todos.html";
}



document.getElementById("go-register").onclick = () => {
    const loginCard = document.getElementById("login-card");
    const registerCard = document.getElementById("register-card");
    loginCard.classList.add("hidden");
    setTimeout(() => {
        loginCard.style.display = "none";
        registerCard.style.display = "block";
    }, 400);
};



document.getElementById("go-login").onclick = () => {
    const registerCard = document.getElementById("register-card");
    const loginCard = document.getElementById("login-card");
    registerCard.classList.add("hidden");
    setTimeout(() => {
        registerCard.style.display = "none";
        loginCard.style.display = "block";
        loginCard.classList.remove("hidden");
    }, 400);
};



document.getElementById("login-btn").addEventListener("click", async () => {
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    if (!email || !password) {
        alert("Veuillez remplir tous les champs");
        return;
    }
    const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (data.token) {
        localStorage.setItem("token", data.token);
        document.body.style.animation = "fadeOut 0.6s ease-out forwards";
        setTimeout(() => {
            window.location.href = "todos.html";
        }, 600);
    } else {
        alert(data.msg);
    }
});



document.getElementById("register-btn").addEventListener("click", async () => {
    const firstname = document.getElementById("reg-firstname").value.trim();
    const name = document.getElementById("reg-name").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    if (!firstname || !name || !email || !password) {
        alert("Veuillez remplir tous les champs");
        return;
    }
    if (password.length < 6) {
        alert("Le mot de passe doit contenir au moins 6 caractères");
        return;
    }
    const res = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, name, firstname })
    });
    const data = await res.json();
    if (data.token) {
        localStorage.setItem("token", data.token);
        document.body.style.animation = "fadeOut 0.6s ease-out forwards";
        setTimeout(() => {
            window.location.href = "todos.html";
        }, 600);
    } else {
        alert(data.msg);
    }
});