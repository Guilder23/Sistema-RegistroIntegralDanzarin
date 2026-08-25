document.addEventListener('DOMContentLoaded', function () {
    const notificacionesBtn = document.getElementById('notificacionesBtn');
    const notificacionesDropdown = document.getElementById('notificacionesDropdown');
    const usuarioBtn = document.getElementById('usuarioBtn');
    const usuarioDropdown = document.getElementById('usuarioDropdown');

    if (notificacionesBtn && notificacionesDropdown) {
        notificacionesBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            usuarioDropdown?.classList.remove('show');
            notificacionesDropdown.classList.toggle('show');
        });
    }

    if (usuarioBtn && usuarioDropdown) {
        usuarioBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            notificacionesDropdown?.classList.remove('show');
            usuarioDropdown.classList.toggle('show');
        });
    }

    document.addEventListener('click', function () {
        notificacionesDropdown?.classList.remove('show');
        usuarioDropdown?.classList.remove('show');
    });
});
