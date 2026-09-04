document.addEventListener('DOMContentLoaded', function () {
    const asociacionSelect = document.getElementById('editarDanzarinAsociacion');
    const conjuntoSelect = document.getElementById('editarDanzarinConjunto');
    const bloqueSelect = document.getElementById('editarDanzarinBloque');
    const filtrar = function (select, attribute, value) {
        if (!select) return;
        Array.from(select.options).forEach(option => {
            const visible = !option.value || option.dataset[attribute] === value;
            option.hidden = !visible;
            option.disabled = !visible;
        });
        if (select.selectedOptions[0]?.disabled) select.value = '';
    };
    const actualizarBloques = function () { filtrar(bloqueSelect, 'conjuntoId', conjuntoSelect?.value || ''); };
    const actualizarConjuntos = function () {
        if (asociacionSelect) filtrar(conjuntoSelect, 'asociacionId', asociacionSelect.value);
        actualizarBloques();
    };
    asociacionSelect?.addEventListener('change', actualizarConjuntos);
    conjuntoSelect?.addEventListener('change', actualizarBloques);
    const modalEditar = document.getElementById('modalEditarDanzarin');
    if (!modalEditar) return;

    modalEditar.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const id = button.getAttribute('data-id');
        const setVal = (idName, val) => { const el = document.getElementById(idName); if (!el) return; el.value = val; };
        const setValOr = (idName, attrName, fallback='') => setVal(idName, button.getAttribute(attrName) || fallback);
        setValOr('editarNombre', 'data-nombre', '');
        setValOr('editarApellidoPaterno', 'data-apellido-paterno', '');
        setValOr('editarApellidoMaterno', 'data-apellido-materno', '');
        setValOr('editarEmail', 'data-email', '');
        setValOr('editarTelefono', 'data-telefono', '');
        setValOr('editarCiudad', 'data-ciudad', '');
        setValOr('editarDireccion', 'data-direccion', '');
        setValOr('editarObservacion', 'data-observacion', '');
        setValOr('editarCarnetCi', 'data-carnet-ci', '');
        setValOr('editarCarnetComplemento', 'data-carnet-complemento', '');
        setValOr('editarFechaNacimiento', 'data-fecha-nacimiento', '');
        const formEl = document.getElementById('formEditarDanzarin');
        if (formEl) formEl.action = `/danzarines/${id}/editar/`;
        setVal('editarDanzarinAsociacionNombre', button.getAttribute('data-asociacion') || '');
        setVal('editarDanzarinConjuntoNombre', button.getAttribute('data-conjunto') || '');
        if (asociacionSelect) asociacionSelect.value = button.getAttribute('data-asociacion-id') || '';
        if (conjuntoSelect) conjuntoSelect.value = button.getAttribute('data-conjunto-id') || '';
        setVal('editarDanzarinBloque', button.getAttribute('data-bloque-id') || '');
        actualizarConjuntos();
        setVal('editarDanzarinBloque', button.getAttribute('data-bloque-id') || '');
    });
    // Fallback: también poblar al hacer click en el botón (compatibilidad sin dependencia de eventos de Bootstrap)
    document.querySelectorAll('.btn-editar-danzarin').forEach(btn => {
        btn.addEventListener('click', function (e) {
            const button = e.currentTarget;
            const id = button.getAttribute('data-id');
            const setVal = (idName, val) => { const el = document.getElementById(idName); if (!el) return; el.value = val; };
            const setValOr = (idName, attrName, fallback='') => setVal(idName, button.getAttribute(attrName) || fallback);
            setValOr('editarNombre', 'data-nombre', '');
            setValOr('editarApellidoPaterno', 'data-apellido-paterno', '');
            setValOr('editarApellidoMaterno', 'data-apellido-materno', '');
            setValOr('editarEmail', 'data-email', '');
            setValOr('editarTelefono', 'data-telefono', '');
            setValOr('editarCiudad', 'data-ciudad', '');
            setValOr('editarDireccion', 'data-direccion', '');
            setValOr('editarObservacion', 'data-observacion', '');
            setValOr('editarCarnetCi', 'data-carnet-ci', '');
            setValOr('editarCarnetComplemento', 'data-carnet-complemento', '');
            setValOr('editarFechaNacimiento', 'data-fecha-nacimiento', '');
            const formEl = document.getElementById('formEditarDanzarin');
            if (formEl) formEl.action = `/danzarines/${id}/editar/`;
            setVal('editarDanzarinAsociacionNombre', button.getAttribute('data-asociacion') || '');
            setVal('editarDanzarinConjuntoNombre', button.getAttribute('data-conjunto') || '');
            if (asociacionSelect) asociacionSelect.value = button.getAttribute('data-asociacion-id') || '';
            if (conjuntoSelect) conjuntoSelect.value = button.getAttribute('data-conjunto-id') || '';
            setVal('editarDanzarinBloque', button.getAttribute('data-bloque-id') || '');
            actualizarConjuntos();
            setVal('editarDanzarinBloque', button.getAttribute('data-bloque-id') || '');
        });
    });
});
