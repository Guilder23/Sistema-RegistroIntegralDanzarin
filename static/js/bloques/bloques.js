document.addEventListener('DOMContentLoaded', function () {
    const editarForm = document.getElementById('formEditarBloque');
    if (editarForm) {
        document.querySelectorAll('[data-target="#modalEditarBloque"]').forEach(function (button) {
            button.addEventListener('click', function () {
                editarForm.action = '/bloques/' + button.dataset.id + '/editar/';
                document.getElementById('editarBloqueNombre').value = button.dataset.nombre || '';
                document.getElementById('editarBloqueDescripcion').value = button.dataset.descripcion || '';
                document.getElementById('editarBloqueActivo').checked = button.dataset.activo === '1';
                const conjuntoSelect = document.getElementById('editarBloqueConjunto');
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
        });
    });

    const asociacionSelect = document.getElementById('crearBloqueAsociacion');
    const conjuntoSelect = document.getElementById('crearBloqueConjunto');
    if (asociacionSelect && conjuntoSelect) {
        const filterByAsociacion = function () {
            const asociacionId = asociacionSelect.value;
            Array.from(conjuntoSelect.options).forEach(function (option) {
                option.hidden = option.dataset.asociacion !== asociacionId;
                option.disabled = option.hidden;
            });
            const visibleOptions = Array.from(conjuntoSelect.options).filter(function (option) {
                return !option.hidden;
            });
            if (visibleOptions.length) {
                conjuntoSelect.value = visibleOptions[0].value;
            }
        };
        asociacionSelect.addEventListener('change', filterByAsociacion);
        filterByAsociacion();
    }
});
