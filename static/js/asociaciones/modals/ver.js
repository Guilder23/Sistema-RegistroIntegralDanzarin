document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-target="#modalVerAsociacion"]').forEach(function (button) {
        button.addEventListener('click', function () {
            document.getElementById('verAsociacionNombre').textContent = button.dataset.nombre;
            document.getElementById('verAsociacionConjuntos').textContent = button.dataset.conjuntos;
            document.getElementById('verAsociacionIntegrantes').textContent = button.dataset.integrantes;
        });
    });
});
