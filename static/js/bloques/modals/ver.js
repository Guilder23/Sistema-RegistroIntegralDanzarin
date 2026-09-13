document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-target="#modalVerBloque"]').forEach(function (button) {
        button.addEventListener('click', function () {
            document.getElementById('verBloqueNombre').textContent = button.dataset.nombre || '';
            document.getElementById('verBloqueConjunto').textContent = button.dataset.conjunto || '';
            document.getElementById('verBloqueAsociacion').textContent = button.dataset.asociacion || '';
            document.getElementById('verBloqueDescripcion').textContent = button.dataset.descripcion || 'Sin descripción';
            document.getElementById('verBloqueCreadoPor').textContent = button.dataset.creadoPor || 'No disponible';
        });
    });
});
