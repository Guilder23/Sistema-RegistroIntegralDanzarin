document.addEventListener('DOMContentLoaded', function () {
    const asociacionSelect = document.getElementById('editarSocioAsociacion');
    const conjuntoSelect = document.getElementById('editarSocioConjunto');
    const bloqueSelect = document.getElementById('editarSocioBloque');
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
    const modalEditar = document.getElementById('modalEditarSocio');
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
        const formEl = document.getElementById('formEditarSocio');
        if (formEl) formEl.action = `/socios/${id}/editar/`;
        setVal('editarSocioAsociacionNombre', button.getAttribute('data-asociacion') || '');
        setVal('editarSocioConjuntoNombre', button.getAttribute('data-conjunto') || '');
        if (asociacionSelect) asociacionSelect.value = button.getAttribute('data-asociacion-id') || '';
        if (conjuntoSelect) conjuntoSelect.value = button.getAttribute('data-conjunto-id') || '';
        setVal('editarSocioBloque', button.getAttribute('data-bloque-id') || '');
        actualizarConjuntos();
        setVal('editarSocioBloque', button.getAttribute('data-bloque-id') || '');
    });
    // Fallback: también poblar al hacer click en el botón (compatibilidad sin dependencia de eventos de Bootstrap)
    document.querySelectorAll('.btn-editar-socio').forEach(btn => {
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
            const formEl = document.getElementById('formEditarSocio');
            if (formEl) formEl.action = `/socios/${id}/editar/`;
            setVal('editarSocioAsociacionNombre', button.getAttribute('data-asociacion') || '');
            setVal('editarSocioConjuntoNombre', button.getAttribute('data-conjunto') || '');
            if (asociacionSelect) asociacionSelect.value = button.getAttribute('data-asociacion-id') || '';
            if (conjuntoSelect) conjuntoSelect.value = button.getAttribute('data-conjunto-id') || '';
            setVal('editarSocioBloque', button.getAttribute('data-bloque-id') || '');
            actualizarConjuntos();
            setVal('editarSocioBloque', button.getAttribute('data-bloque-id') || '');
        });
    });
});
