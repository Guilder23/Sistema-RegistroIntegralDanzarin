document.addEventListener('DOMContentLoaded', function () {
    const eliminarForm = document.getElementById('formEliminarConjunto');
    document.querySelectorAll('.btn-eliminar-conjunto').forEach(function (button) {
        button.addEventListener('click', function () {
            eliminarForm.action = '/conjuntos/' + button.dataset.id + '/eliminar/';
            document.getElementById('eliminarConjuntoNombre').textContent = button.dataset.nombre;
        });
    });
});
