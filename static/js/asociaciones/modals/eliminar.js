document.addEventListener('DOMContentLoaded', function () {
    const eliminarForm = document.getElementById('formEliminarAsociacion');
    document.querySelectorAll('.btn-eliminar-asociacion').forEach(function (button) {
        button.addEventListener('click', function () {
            eliminarForm.action = '/asociaciones/' + button.dataset.id + '/eliminar/';
            document.getElementById('eliminarAsociacionNombre').textContent = button.dataset.nombre;
        });
    });
});
