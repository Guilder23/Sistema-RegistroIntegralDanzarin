/* ================================================
   FOOTER INICIO - FUNCIONALIDADES Y EVENTOS
   ================================================ */

document.addEventListener('DOMContentLoaded', function () {
    // ===== ELEMENTOS DEL DOM =====
    const footerLinks = document.querySelectorAll('.footer-links a');
    const socialLinks = document.querySelectorAll('.social-link');
    const footer = document.querySelector('.footer-inicio');

    // ===== ANIMACIÓN DE ENTRADA DEL FOOTER =====
    if (footer) {
        footer.style.opacity = '0';
        footer.style.transform = 'translateY(40px)';
        
        // Esperar a que el footer esté en vista
        const footerObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.dataset.animated) {
                    entry.target.dataset.animated = 'true';
                    entry.target.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    footerObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        footerObserver.observe(footer);
    }

    // ===== HOVER EFFECTS EN ENLACES DEL FOOTER =====
    footerLinks.forEach(link => {
        link.addEventListener('mouseenter', function () {
            this.style.transition = 'all 0.3s ease';
            this.style.paddingLeft = '0.75rem';
            this.style.color = '#fbbf24';
        });

        link.addEventListener('mouseleave', function () {
            this.style.paddingLeft = '0';
            this.style.color = 'rgba(255, 255, 255, 0.85)';
        });

        // Feedback visual en click
        link.addEventListener('click', function (e) {
            if (this.href === '#') {
                e.preventDefault();
            }

            // Crear ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.position = 'absolute';
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(251, 191, 36, 0.4)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'footer-ripple 0.6s ease-out';
            ripple.style.pointerEvents = 'none';

            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        });
    });

    // ===== ANIMACIONES EN REDES SOCIALES =====
    socialLinks.forEach((link, index) => {
        link.addEventListener('mouseenter', function () {
            this.style.transition = 'all 0.3s ease';
            this.style.transform = 'translateY(-5px) scale(1.1)';
        });

        link.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0) scale(1)';
        });

        // Agregar animación de carga
        link.style.opacity = '0';
        link.style.transform = 'scale(0.8)';
        setTimeout(() => {
            link.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            link.style.opacity = '1';
            link.style.transform = 'scale(1)';
        }, 300 + (index * 100));
    });

    // ===== COPIAR EMAIL AL CLIPBOARD =====
    const emailLink = document.querySelector('.footer-links a[href^="mailto:"]');
    if (emailLink) {
        emailLink.addEventListener('click', function (e) {
            const email = this.getAttribute('href').replace('mailto:', '');
            const originalText = this.textContent;

            // Copiar al portapapeles
            navigator.clipboard.writeText(email).then(() => {
                const icon = this.querySelector('i');
                const originalIcon = icon.className;

                // Cambiar icono a checkmark
                icon.className = 'fas fa-check';
                this.style.color = '#34d399';

                setTimeout(() => {
                    icon.className = originalIcon;
                    this.style.color = '#fbbf24';
                }, 2000);
            });
        });
    }

    // ===== CONTADOR DE SECCIONES ANIMADO =====
    const footerSections = document.querySelectorAll('.footer-section');
    footerSections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, 100 + (index * 100));
    });

    // ===== SMOOTH SCROLL PARA ENLACES INTERNOS =====
    document.querySelectorAll('.footer-links a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && document.querySelector(href)) {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ===== INFORMACIÓN DEL FOOTER VISIBLE =====
    const footerInfo = document.querySelector('.footer-copyright');
    if (footerInfo) {
        footerInfo.style.opacity = '0';
        setTimeout(() => {
            footerInfo.style.transition = 'opacity 0.8s ease 0.4s';
            footerInfo.style.opacity = '1';
        }, 100);
    }

    // ===== DETECTAR YEAR Y ACTUALIZAR DINÁMICAMENTE =====
    const yearElement = document.querySelector('.footer-copyright');
    if (yearElement) {
        const year = new Date().getFullYear();
        yearElement.textContent = yearElement.textContent.replace(/2026/, year);
    }
});

// ===== CREAR ESTILOS NECESARIOS PARA ANIMACIONES =====
if (!document.querySelector('style[data-footer-styles]')) {
    const style = document.createElement('style');
    style.setAttribute('data-footer-styles', 'true');
    style.textContent = `
        @keyframes footer-ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }

        .footer-links a {
            position: relative;
        }

        .social-link {
            position: relative;
            overflow: hidden;
        }
    `;
    document.head.appendChild(style);
}
