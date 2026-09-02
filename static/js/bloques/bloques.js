document.addEventListener('DOMContentLoaded', function () {
    const editarForm = document.getElementById('formEditarBloque');
    const filtrarConjuntos = function (asociacionSelect, conjuntoSelect) {
        if (!asociacionSelect || !conjuntoSelect) return;
        Array.from(conjuntoSelect.options).forEach(function (option) {
            const visible = option.dataset.asociacion === asociacionSelect.value;
            option.hidden = !visible;
            option.disabled = !visible;
        });
        if (conjuntoSelect.selectedOptions[0]?.disabled) conjuntoSelect.value = '';
    };

    const crearAsociacion = document.getElementById('crearBloqueAsociacion');
    const crearConjunto = document.getElementById('crearBloqueConjunto');
    if (crearAsociacion && crearConjunto) {
        crearAsociacion.addEventListener('change', function () {
            filtrarConjuntos(crearAsociacion, crearConjunto);
        });
        filtrarConjuntos(crearAsociacion, crearConjunto);
    }

    const editarAsociacion = document.getElementById('editarBloqueAsociacion');
    const editarConjunto = document.getElementById('editarBloqueConjunto');
    if (editarAsociacion && editarConjunto) {
        editarAsociacion.addEventListener('change', function () {
            filtrarConjuntos(editarAsociacion, editarConjunto);
        });
    }

    if (editarForm) {
        document.querySelectorAll('[data-target="#modalEditarBloque"]').forEach(function (button) {
            button.addEventListener('click', function () {
                editarForm.action = '/bloques/' + button.dataset.id + '/editar/';
                document.getElementById('editarBloqueNombre').value = button.dataset.nombre || '';
                document.getElementById('editarBloqueDescripcion').value = button.dataset.descripcion || '';
                document.getElementById('editarBloqueActivo').checked = button.dataset.activo === '1';
                const conjuntoSelect = document.getElementById('editarBloqueConjunto');
                if (editarAsociacion) {
                    editarAsociacion.value = button.dataset.asociacionId || '';
                    filtrarConjuntos(editarAsociacion, conjuntoSelect);
                }
                if (conjuntoSelect) {
                    conjuntoSelect.value = button.dataset.conjuntoId || conjuntoSelect.options[0]?.value || '';
                }
            });
        });
    }

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
