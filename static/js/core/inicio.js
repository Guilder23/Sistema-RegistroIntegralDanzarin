/* ================================================
   PÁGINA INICIO - JavaScript Específico
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    initializePaginationAnimations();
    initializeFaqAccordion();
    initializeRevealAnimations();
    initializeFechaNacimientoMode();
    initializeConfirmationModal();
    initializeFormularioAjax();
    initializeImageFallAnimations();
    initializeHashNavigation();
});

function initializeHashNavigation() {
    const openModalFromHash = () => {
        if (window.location.hash !== '#modalInscripcion') return;

        const modal = document.getElementById('modalInscripcion');
        if (!modal || typeof $ === 'undefined') return;

        $(modal).modal('show');
    };

    openModalFromHash();
    window.addEventListener('hashchange', openModalFromHash);
}

function initializePaginationAnimations() {
    document.querySelectorAll('.pagination a').forEach(link => {
        link.addEventListener('click', function() {
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 180);
        });
    });
}

function initializeFaqAccordion() {
    document.querySelectorAll('.faq-item').forEach(item => {
        const button = item.querySelector('.faq-question');
        if (!button) return;

        button.addEventListener('click', () => {
            const wasActive = item.classList.contains('active');

            document.querySelectorAll('.faq-item').forEach(faqItem => {
                faqItem.classList.remove('active');
                const faqButton = faqItem.querySelector('.faq-question');
                if (faqButton) {
                    faqButton.setAttribute('aria-expanded', 'false');
                }
            });

            if (!wasActive) {
                item.classList.add('active');
                button.setAttribute('aria-expanded', 'true');
            }
        });
    });
}

function initializeRevealAnimations() {
    const elements = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window) || elements.length === 0) {
        elements.forEach(el => el.classList.add('visible'));
        return;
    }

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                obs.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.12
    });

    elements.forEach(el => observer.observe(el));
}

function initializeFechaNacimientoMode() {
    const dateInput = document.getElementById('fecha_nacimiento');
    const manualInput = document.getElementById('fecha_nacimiento_manual');
    const calendarBtn = document.getElementById('fechaNacimientoBtn');
    const errorFeedback = document.getElementById('fechaNacimientoError');

    if (!dateInput || !manualInput || !calendarBtn) return;

    const isMobileMode = () => window.innerWidth <= 768 || 'ontouchstart' in window;

    const formatDate = date => {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    };

    const parseDate = value => {
        const match = value.trim().match(/^([0-3]\d)\/([0-1]\d)\/(\d{4})$/);
        if (!match) return null;
        const day = Number(match[1]);
        const month = Number(match[2]);
        const year = Number(match[3]);
        const date = new Date(year, month - 1, day);
        return date.getFullYear() === year && date.getMonth() + 1 === month && date.getDate() === day ? date : null;
    };

    const showError = message => {
        if (errorFeedback) {
            errorFeedback.textContent = message;
            errorFeedback.style.display = 'block';
        }
        manualInput.classList.add('is-invalid');
    };

    const clearError = () => {
        if (errorFeedback) {
            errorFeedback.style.display = 'none';
        }
        manualInput.classList.remove('is-invalid');
    };

    const setMobileMode = active => {
        if (active) {
            dateInput.style.position = 'absolute';
            dateInput.style.left = '-9999px';
            dateInput.style.width = '1px';
            dateInput.style.height = '1px';
            dateInput.style.opacity = '0';
            dateInput.style.pointerEvents = 'none';
            manualInput.classList.remove('d-none');
            calendarBtn.classList.remove('d-none');
            if (dateInput.value) {
                const date = new Date(dateInput.value);
                if (!Number.isNaN(date.getTime())) {
                    manualInput.value = formatDate(date);
                }
            }
        } else {
            dateInput.style.position = '';
            dateInput.style.left = '';
            dateInput.style.width = '';
            dateInput.style.height = '';
            dateInput.style.opacity = '';
            dateInput.style.pointerEvents = '';
            manualInput.classList.add('d-none');
            calendarBtn.classList.add('d-none');
            if (manualInput.value) {
                const date = parseDate(manualInput.value);
                if (date) {
                    dateInput.value = date.toISOString().slice(0, 10);
                    clearError();
                }
            }
        }
    };

    const updateMode = () => setMobileMode(isMobileMode());
    updateMode();
    window.addEventListener('resize', updateMode);

    calendarBtn.addEventListener('click', () => {
        dateInput.focus();
        dateInput.click();
    });

    dateInput.addEventListener('input', () => {
        if (!dateInput.value) {
            manualInput.value = '';
            clearError();
            return;
        }
        const date = new Date(dateInput.value);
        if (!Number.isNaN(date.getTime())) {
            manualInput.value = formatDate(date);
            clearError();
        }
    });

    manualInput.addEventListener('blur', () => {
        if (!manualInput.value.trim()) {
            dateInput.value = '';
            clearError();
            return;
        }
        const date = parseDate(manualInput.value);
        if (date) {
            dateInput.value = date.toISOString().slice(0, 10);
            clearError();
        } else {
            dateInput.value = '';
            showError('Formato dd/mm/aaaa válido.');
        }
    });
}

// Scroll suave para anclas
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const targetSelector = this.getAttribute('href');
        if (!targetSelector || targetSelector === '#') return;

        const target = document.querySelector(targetSelector);
        if (!target) return;

        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});

// ================================================
// MODAL DE CONFIRMACIÓN CON EFECTO DE EXPLOSIÓN
// ================================================

function initializeConfirmationModal() {
    // Verificar si hay mensaje de éxito de Django con el marcador especial
    const successMessages = document.querySelectorAll('.alert-success');
    
    successMessages.forEach(message => {
        const messageText = message.textContent || message.innerText;
        if (messageText.includes('CONFETTI_SHOW') || messageText.includes('solicitud fue registrada')) {
            // Ocultar el mensaje original de Django
            message.style.display = 'none';
            
            // Mostrar el modal personalizado con confeti
            showConfirmationModal();
        }
    });
}

function showConfirmationModal() {
    const modal = document.getElementById('modalConfirmacion');
    if (!modal) return;
    
    // Mostrar el modal
    $(modal).modal('show');
    
    // Crear efecto de confeti
    createConfetti();
}

function createConfetti() {
    const colors = ['#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#8b5cf6', '#ec4899'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.width = (Math.random() * 10 + 5) + 'px';
            confetti.style.height = (Math.random() * 10 + 5) + 'px';
            confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
            
            document.body.appendChild(confetti);
            
            // Eliminar el confeti después de la animación
            setTimeout(() => {
                confetti.remove();
            }, 4000);
        }, i * 50);
    }
}

// ================================================
// ENVÍO DEL FORMULARIO POR AJAX (SIN RECARGAR)
// ================================================

function initializeFormularioAjax() {
    const form = document.getElementById('formInscripcion');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Enviando...';

            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                // Si la respuesta es OK, mostramos el modal de confirmación
                $('#modalInscripcion').modal('hide');
                showConfirmationModal();
                form.reset();
            })
            .catch(error => {
                // Si hay error, intentamos el comportamiento por defecto
                console.error('Error en el envío:', error);
                form.submit();
            })
            .finally(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            });
        } else {
            form.submit();
        }
    });
}

// ================================================
// ANIMACIONES DE CAÍDA PARA IMÁGENES (Viewport)
// ================================================

function initializeImageFallAnimations() {
    const images = document.querySelectorAll('.img-fall');
    if (images.length === 0) return;

    if (!('IntersectionObserver' in window)) {
        images.forEach(img => img.classList.add('img-fall-visible'));
        return;
    }

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach((entry, idx) => {
            if (entry.isIntersecting) {
                const img = entry.target;
                // Calcular delay basado en el índice dentro del contenedor padre
                const siblings = Array.from(img.parentElement.querySelectorAll('.img-fall'));
                const siblingIndex = siblings.indexOf(img);
                const delay = Math.min(siblingIndex * 0.1, 0.5);
                
                setTimeout(() => {
                    img.classList.add('img-fall-visible');
                }, delay * 1000);
                
                obs.unobserve(img);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    images.forEach(img => observer.observe(img));
}
