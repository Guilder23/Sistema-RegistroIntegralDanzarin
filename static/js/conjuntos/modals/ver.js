document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-target="#modalVerConjunto"]').forEach(function (button) {
        button.addEventListener('click', function () {
            document.getElementById('verConjuntoNombre').textContent = button.dataset.nombre;
            document.getElementById('verConjuntoAsociacion').textContent = button.dataset.asociacion;
        });
    });
});
