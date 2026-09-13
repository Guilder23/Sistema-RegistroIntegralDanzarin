document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-target="#modalEditarAsociacion"]').forEach(function (button) {
        button.addEventListener('click', function () {
            document.getElementById('formEditarAsociacion').action = '/asociaciones/' + button.dataset.id + '/editar/';
            document.getElementById('editarAsociacionNombre').value = button.dataset.nombre;
            document.getElementById('editarAsociacionActivo').checked = button.dataset.activo === '1';
        });
    });
});
