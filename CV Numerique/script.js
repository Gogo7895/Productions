const rocketContainer = document.querySelector('.rocket-container');
const rocketImg = document.getElementById('rocket-img');
const galaxy = document.getElementById('galaxy');
const planets = document.querySelectorAll('.planet');

// 1. Pour forcer l'arrivée tout en bas au chargement
window.addEventListener('load', () => {
    window.scrollTo(0, document.body.scrollHeight);
});

// 2. Pour la gestion du scroll et des animations
let lastScrollTop = 0;

window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    const maxScroll = document.body.scrollHeight - window.innerHeight;
    const percent = scrollY / maxScroll;

    // Pour le déplacement de la fusée
    rocketContainer.style.bottom = (10 + (1 - percent) * 75) + '%';

    // Pour la rotation de la galaxie
    if (galaxy) {
        galaxy.style.transform = `translate(-50%, -50%) rotate(${scrollY * 0.005}deg) scale(${1 + (1 - percent) * 0.2})`;
    }

    // Pour l'inclinaison de la fusée
    if (scrollY > lastScrollTop) {
        rocketImg.style.transform = 'rotate(10deg)';
    } else {
        rocketImg.style.transform = 'rotate(-10deg)';
    }
    lastScrollTop = scrollY;
});

// 3. Pour l'apparition fluide des planètes
const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'scale(1)';
        } else {
            entry.target.style.opacity = '0';
            entry.target.style.transform = 'scale(0.8)';
        }
    });
}, { threshold: 0.2 });

planets.forEach(p => {
    p.style.opacity = '0';
    p.style.transform = 'scale(0.8)';
    observer.observe(p);
});

// 4. Les étoiles
const starsContainer = document.querySelector('.stars');
for (let i = 0; i < 150; i++) {
    const star = document.createElement('div');
    star.classList.add('star');
    star.style.top = Math.random() * 100 + 'vh';
    star.style.left = Math.random() * 100 + 'vw';
    star.style.animationDelay = Math.random() * 2 + 's';
    starsContainer.appendChild(star);
}