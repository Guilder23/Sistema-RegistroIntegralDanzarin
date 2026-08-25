/* ============================================================================
   NAVBAR JS - Interacciones del Menú de Usuario y Notificaciones
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function () {
    const usuarioBtn = document.getElementById('usuarioBtn');
    const usuarioDropdown = document.getElementById('usuarioDropdown');

    if (usuarioBtn && usuarioDropdown) {
        usuarioBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            const isShown = usuarioDropdown.classList.contains('show');
            usuarioDropdown.classList.toggle('show');
            usuarioBtn.setAttribute('aria-expanded', !isShown);
        });

        document.addEventListener('click', function (e) {
            if (!usuarioDropdown.contains(e.target) && !usuarioBtn.contains(e.target)) {
                usuarioDropdown.classList.remove('show');
                usuarioBtn.setAttribute('aria-expanded', 'false');
            }
        });

        // Cerrar con Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && usuarioDropdown.classList.contains('show')) {
                usuarioDropdown.classList.remove('show');
                usuarioBtn.setAttribute('aria-expanded', 'false');
            }
        });
    }
});
