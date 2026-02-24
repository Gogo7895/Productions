// Données des posts
let posts = [{
        id: 1,
        author: "Dr. Marie Dubois",
        initials: "MD",
        specialty: "Cardiologue",
        time: "Il y a 2 heures",
        content: "Nouvelle étude intéressante sur les traitements cardiaques. Les résultats sont prometteurs.",
        likes: 12,
        comments: 3,
        liked: false
    },
    {
        id: 2,
        author: "Dr. Pierre Martin",
        initials: "PM",
        specialty: "Chirurgien",
        time: "Il y a 5 heures",
        content: "Retour d'expérience positif sur une nouvelle technique chirurgicale.",
        likes: 8,
        comments: 2,
        liked: false
    }
];

let currentEditId = null;
let currentConversationId = null;

// Données des conversations
let conversations = [{
        id: 1,
        name: "Dr. Marie Dubois",
        specialty: "Cardiologue",
        initials: "MD",
        lastMessage: "Merci pour l'étude !",
        timestamp: "10:30",
        unread: 2,
        messages: [
            { id: 1, text: "Bonjour! Comment allez-vous?", own: false, time: "10:15" },
            { id: 2, text: "Bien, merci! J'ai lu ton article", own: true, time: "10:20" },
            { id: 3, text: "Merci pour l'étude !", own: false, time: "10:30" }
        ]
    },
    {
        id: 2,
        name: "Dr. Pierre Martin",
        specialty: "Chirurgien",
        initials: "PM",
        lastMessage: "À bientôt !",
        timestamp: "09:45",
        unread: 1,
        messages: [
            { id: 1, text: "As-tu du temps pour un appel?", own: false, time: "09:30" },
            { id: 2, text: "Oui, bien sûr! Quand?", own: true, time: "09:40" },
            { id: 3, text: "À bientôt !", own: false, time: "09:45" }
        ]
    },
    {
        id: 3,
        name: "Dr. Sophie Laurent",
        specialty: "Neurologue",
        initials: "SL",
        lastMessage: "Intéressant !",
        timestamp: "hier",
        unread: 0,
        messages: [
            { id: 1, text: "Avez-vous des cas similaires?", own: false, time: "hier 14:20" },
            { id: 2, text: "Oui, j'en ai quelques-uns", own: true, time: "hier 15:00" }
        ]
    }
];

// Connexion
function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('emailInput').value;
    const password = document.getElementById('passwordInput').value;
    const errorMsg = document.getElementById('errorMessage');

    // Vérification simple (identifiants de démo)
    if (email === 'demo@medlinka.com' && password === 'demo123') {
        document.getElementById('loginPage').classList.add('hidden');
        document.getElementById('mainApp').classList.remove('hidden');
        showPosts();
    } else {
        errorMsg.textContent = '❌ Email ou mot de passe incorrect';
        errorMsg.classList.remove('hidden');
    }
}

// Déconnexion
function logout() {
    if (confirm('Voulez-vous vous déconnecter ?')) {
        document.getElementById('mainApp').classList.add('hidden');
        document.getElementById('loginPage').classList.remove('hidden');
        document.getElementById('loginForm').reset();
    }
}

// Afficher les posts
function showPosts() {
    const container = document.getElementById('postsContainer');

    if (posts.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:var(--light-text)">Aucun post pour le moment.</p>';
        return;
    }

    container.innerHTML = posts.map(post => `
        <div class="post-card">
            <div class="post-header">
                <div class="avatar">${post.initials}</div>
                <div class="post-info">
                    <div class="post-author">${post.author}</div>
                    <div class="post-specialty">${post.specialty}</div>
                    <div class="post-time">${post.time}</div>
                </div>
                <div class="post-actions">
                    <button class="post-btn" onclick="editPost(${post.id})">✏️</button>
                    <button class="post-btn" onclick="deletePost(${post.id})">🗑️</button>
                </div>
            </div>
            
            <div class="post-content">${post.content}</div>
            
            <div class="post-stats">
                <span>${post.likes} réactions</span>
                <span>${post.comments} commentaires</span>
            </div>
            
            <div class="post-interactions">
                <button class="interact-btn ${post.liked ? 'liked' : ''}" onclick="likePost(${post.id})">
                    👍 J'aime
                </button>
                <button class="interact-btn">💬 Commenter</button>
                <button class="interact-btn">📤 Partager</button>
            </div>
        </div>
    `).join('');
}

// Ouvrir le modal pour créer un post
function openModal() {
    currentEditId = null;
    document.getElementById('modalTitle').textContent = 'Créer un post';
    document.getElementById('postForm').reset();
    document.getElementById('postModal').classList.remove('hidden');
}

// Fermer le modal
function closeModal() {
    document.getElementById('postModal').classList.add('hidden');
    currentEditId = null;
}

// Sauvegarder un post
function savePost(event) {
    event.preventDefault();

    const author = document.getElementById('authorInput').value;
    const specialty = document.getElementById('specialtyInput').value;
    const content = document.getElementById('contentInput').value;

    if (currentEditId) {
        // Modifier un post existant
        const post = posts.find(p => p.id === currentEditId);
        post.author = author;
        post.specialty = specialty;
        post.content = content;
        post.initials = getInitials(author);
    } else {
        // Créer un nouveau post
        const newPost = {
            id: Date.now(),
            author: author,
            initials: getInitials(author),
            specialty: specialty,
            time: "À l'instant",
            content: content,
            likes: 0,
            comments: 0,
            liked: false
        };
        posts.unshift(newPost);
    }

    showPosts();
    closeModal();
}

// Modifier un post
function editPost(id) {
    const post = posts.find(p => p.id === id);
    if (!post) return;

    currentEditId = id;
    document.getElementById('modalTitle').textContent = 'Modifier le post';
    document.getElementById('authorInput').value = post.author;
    document.getElementById('specialtyInput').value = post.specialty;
    document.getElementById('contentInput').value = post.content;
    document.getElementById('postModal').classList.remove('hidden');
}

// Supprimer un post
function deletePost(id) {
    if (confirm('Voulez-vous supprimer ce post ?')) {
        posts = posts.filter(p => p.id !== id);
        showPosts();
    }
}

// Liker un post
function likePost(id) {
    const post = posts.find(p => p.id === id);
    if (post) {
        post.liked = !post.liked;
        post.likes += post.liked ? 1 : -1;
        showPosts();
    }
}

// Obtenir les initiales
function getInitials(name) {
    const words = name.split(' ');
    if (words.length >= 2) {
        return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
}

// Recherche
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const term = e.target.value.toLowerCase();

            if (term === '') {
                showPosts();
                return;
            }

            const filtered = posts.filter(post =>
                post.author.toLowerCase().includes(term) ||
                post.specialty.toLowerCase().includes(term) ||
                post.content.toLowerCase().includes(term)
            );

            const container = document.getElementById('postsContainer');
            if (filtered.length === 0) {
                container.innerHTML = '<p style="text-align:center;color:var(--light-text)">Aucun résultat.</p>';
            } else {
                posts = filtered;
                showPosts();
            }
        });
    }
});

// Changer le thème
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    // Changer l'icône
    const buttons = document.querySelectorAll('.theme-toggle');
    buttons.forEach(btn => {
        btn.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    });
}

// Charger le thème sauvegardé
(function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    const buttons = document.querySelectorAll('.theme-toggle');
    buttons.forEach(btn => {
        btn.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    });
})();

// Fermer le modal en cliquant en dehors
document.addEventListener('click', function(e) {
    const modal = document.getElementById('postModal');
    if (e.target === modal) {
        closeModal();
    }
});

// === MESSAGES FUNCTIONALITY ===

// Afficher la vue des messages
function showMessages() {
    document.getElementById('feedView').classList.add('hidden');
    document.getElementById('messagesView').classList.remove('hidden');
    showConversations();
}

// Retourner à la vue du feed
function showFeed() {
    document.getElementById('messagesView').classList.add('hidden');
    document.getElementById('feedView').classList.remove('hidden');
}

// Afficher la liste des conversations
function showConversations() {
    const container = document.getElementById('conversationsList');

    container.innerHTML = conversations.map(conv => `
        <div class="conversation-item ${currentConversationId === conv.id ? 'active' : ''}" onclick="openConversation(${conv.id})">
            <div class="conversation-avatar">${conv.initials}</div>
            <div class="conversation-info">
                <div class="conversation-name">${conv.name}</div>
                <div class="conversation-preview">${conv.lastMessage}</div>
            </div>
        </div>
    `).join('');
}

// Ouvrir une conversation
function openConversation(conversationId) {
    currentConversationId = conversationId;
    const conversation = conversations.find(c => c.id === conversationId);

    if (!conversation) return;

    // Mettre à jour le header
    document.getElementById('chatAvatar').textContent = conversation.initials;
    document.getElementById('chatUserName').textContent = conversation.name;
    document.getElementById('chatUserSpecialty').textContent = conversation.specialty;

    // Afficher les messages
    displayMessages(conversation);

    // Mettre à jour la liste des conversations
    showConversations();

    // Réinitialiser l'input
    document.getElementById('messageInput').value = '';
    document.getElementById('messageInput').focus();
}

// Afficher les messages de la conversation
function displayMessages(conversation) {
    const display = document.getElementById('messagesDisplay');

    if (conversation.messages.length === 0) {
        display.innerHTML = '<div class="empty-chat">Aucun message. Démarrez la conversation!</div>';
        return;
    }

    display.innerHTML = conversation.messages.map(msg => `
        <div class="message ${msg.own ? 'own' : ''}">
            <div class="message-content">${msg.text}</div>
            <div class="message-time">${msg.time}</div>
        </div>
    `).join('');

    // Scroller vers le bas
    display.scrollTop = display.scrollHeight;
}

// Envoyer un message
function sendMessage() {
    const input = document.getElementById('messageInput');
    const text = input.value.trim();

    if (!text || !currentConversationId) return;

    const conversation = conversations.find(c => c.id === currentConversationId);
    if (!conversation) return;

    const newMessage = {
        id: Date.now(),
        text: text,
        own: true,
        time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    };

    conversation.messages.push(newMessage);
    conversation.lastMessage = text;
    conversation.timestamp = 'À l\'instant';

    input.value = '';
    displayMessages(conversation);
}

// Gérer la touche Entrée pour envoyer
function handleMessageKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Rechercher dans les conversations
document.addEventListener('DOMContentLoaded', function() {
    const searchConversations = document.getElementById('searchConversations');
    if (searchConversations) {
        searchConversations.addEventListener('input', function(e) {
            const term = e.target.value.toLowerCase();

            if (term === '') {
                showConversations();
                return;
            }

            const filtered = conversations.filter(conv =>
                conv.name.toLowerCase().includes(term) ||
                conv.specialty.toLowerCase().includes(term)
            );

            const container = document.getElementById('conversationsList');
            container.innerHTML = filtered.map(conv => `
                <div class="conversation-item" onclick="openConversation(${conv.id})">
                    <div class="conversation-avatar">${conv.initials}</div>
                    <div class="conversation-info">
                        <div class="conversation-name">${conv.name}</div>
                        <div class="conversation-preview">${conv.lastMessage}</div>
                    </div>
                </div>
            `).join('');
        });
    }
});