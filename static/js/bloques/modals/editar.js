document.addEventListener('DOMContentLoaded', function () {
    const editarForm = document.getElementById('formEditarBloque');
    const asociacionSelect = document.getElementById('editarBloqueAsociacion');
    const conjuntoSelect = document.getElementById('editarBloqueConjunto');

    const filtrarConjuntos = function () {
        if (!asociacionSelect || !conjuntoSelect) return;
        Array.from(conjuntoSelect.options).forEach(function (option) {
            const visible = option.dataset.asociacion === asociacionSelect.value;
            option.hidden = !visible;
            option.disabled = !visible;
        });
        if (conjuntoSelect.selectedOptions[0]?.disabled) conjuntoSelect.value = '';
    };

    asociacionSelect?.addEventListener('change', filtrarConjuntos);

    if (!editarForm) return;

    document.querySelectorAll('[data-target="#modalEditarBloque"]').forEach(function (button) {
        button.addEventListener('click', function () {
            editarForm.action = '/bloques/' + button.dataset.id + '/editar/';
            document.getElementById('editarBloqueNombre').value = button.dataset.nombre || '';
            document.getElementById('editarBloqueDescripcion').value = button.dataset.descripcion || '';
            document.getElementById('editarBloqueActivo').checked = button.dataset.activo === '1';
            if (asociacionSelect) {
                asociacionSelect.value = button.dataset.asociacionId || '';
                filtrarConjuntos();
            }
            if (conjuntoSelect) {
                conjuntoSelect.value = button.dataset.conjuntoId || conjuntoSelect.options[0]?.value || '';
            }
        });
    });
});
