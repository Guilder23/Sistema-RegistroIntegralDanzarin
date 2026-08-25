/* ==========================================================================
   INICIO.JS - Club Carnaval Oruro
   Interacciones, navegación por anclas, modal de membresía y animaciones.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    initializeBackToTop();
    initializeHashAndModalNavigation();
    initializeSmoothScroll();
    initializeScrollReveal();
});

/**
 * Control del botón "Volver arriba"
 */
function initializeBackToTop() {
    const backTop = document.getElementById('backTop');
    if (!backTop) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            backTop.classList.add('show');
        } else {
            backTop.classList.remove('show');
        }
    });

    backTop.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Control de navegación por Hash y apertura de modal de membresía
 */
function initializeHashAndModalNavigation() {
    const checkHashAndOpenModal = () => {
        if (window.location.hash === '#modalInscripcion') {
            const modal = document.getElementById('modalInscripcion');
            if (modal && typeof $ !== 'undefined') {
                $(modal).modal('show');
            }
        }
    };

    checkHashAndOpenModal();
    window.addEventListener('hashchange', checkHashAndOpenModal);

    document.querySelectorAll('a[href="#modalInscripcion"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const modal = document.getElementById('modalInscripcion');
            if (modal && typeof $ !== 'undefined') {
                $(modal).modal('show');
            }
        });
    });
}

/**
 * Desplazamiento suave para enlaces ancla internos
 */
function initializeSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetSelector = this.getAttribute('href');
            if (!targetSelector || targetSelector === '#' || targetSelector === '#modalInscripcion' || this.hasAttribute('data-toggle')) {
                return;
            }

            const targetElement = document.querySelector(targetSelector);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Animaciones suaves con IntersectionObserver
 */
function initializeScrollReveal() {
    const revealElements = document.querySelectorAll(
        '.discipline-card, .benefit-card, .testimonial-card, .feature, .stat, .schedule-row'
    );

    if (!revealElements || revealElements.length === 0) return;

    if (!('IntersectionObserver' in window)) {
        revealElements.forEach(el => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        });
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -30px 0px'
    });

    revealElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(element);
    });
}
