document.addEventListener('DOMContentLoaded', function () {
    const eliminarForm = document.getElementById('formEliminarBloque');
    document.querySelectorAll('.btn-eliminar-bloque').forEach(function (button) {
        button.addEventListener('click', function () {
            if (eliminarForm) eliminarForm.action = '/bloques/' + button.dataset.id + '/eliminar/';
            const nombre = document.getElementById('eliminarBloqueNombre');
            if (nombre) nombre.textContent = button.dataset.nombre || '';
        });
    });
});
