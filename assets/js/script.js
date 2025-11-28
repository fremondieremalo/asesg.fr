// 1. Animation Navbar au scroll
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// 2. Animation d'apparition au défilement (Scroll Reveal)
const revealElements = document.querySelectorAll('.reveal');

const revealOnScroll = () => {
    const windowHeight = window.innerHeight;
    const elementVisible = 150;

    revealElements.forEach((reveal) => {
        const elementTop = reveal.getBoundingClientRect().top;
        if (elementTop < windowHeight - elementVisible) {
            reveal.classList.add('active');
        }
    });
};

window.addEventListener('scroll', revealOnScroll);

// 3. Animation des Compteurs (Stats)
const counters = document.querySelectorAll('.counter');
let hasAnimated = false; // Pour ne lancer qu'une seule fois

const animateCounters = () => {
    const sectionStats = document.querySelector('.stats-section');
    const sectionPos = sectionStats.getBoundingClientRect().top;
    const screenPos = window.innerHeight;

    if (sectionPos < screenPos && !hasAnimated) {
        counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            const speed = 200; // Plus c'est haut, plus c'est lent

            const updateCount = () => {
                const count = +counter.innerText;
                const inc = target / speed;

                if (count < target) {
                    counter.innerText = Math.ceil(count + inc);
                    setTimeout(updateCount, 20);
                } else {
                    counter.innerText = target;
                }
            };
            updateCount();
        });
        hasAnimated = true;
    }
};

window.addEventListener('scroll', animateCounters);