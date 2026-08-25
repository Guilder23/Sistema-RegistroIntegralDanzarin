document.addEventListener('DOMContentLoaded', function () {
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
        const editarApellidoLegacy = document.getElementById('editarApellido');
        if (editarApellidoLegacy) editarApellidoLegacy.value = button.getAttribute('data-apellido') || `${button.getAttribute('data-apellido-paterno') || ''} ${button.getAttribute('data-apellido-materno') || ''}`.trim();
        setValOr('editarEmail', 'data-email', '');
        setValOr('editarTelefono', 'data-telefono', '');
        setValOr('editarCiudad', 'data-ciudad', '');
        setValOr('editarDireccion', 'data-direccion', '');
        setValOr('editarObservacion', 'data-observacion', '');
        setValOr('editarCarnetCi', 'data-carnet-ci', '');
        setValOr('editarCarnetComplemento', 'data-carnet-complemento', '');
        setValOr('editarFechaNacimiento', 'data-fecha-nacimiento', '');
        setValOr('editarRazon', 'data-razon', '');
        const formEl = document.getElementById('formEditarSocio');
        if (formEl) formEl.action = `/socios/${id}/editar/`;
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
            const editarApellidoLegacy = document.getElementById('editarApellido');
            if (editarApellidoLegacy) editarApellidoLegacy.value = button.getAttribute('data-apellido') || `${button.getAttribute('data-apellido-paterno') || ''} ${button.getAttribute('data-apellido-materno') || ''}`.trim();
            setValOr('editarEmail', 'data-email', '');
            setValOr('editarTelefono', 'data-telefono', '');
            setValOr('editarCiudad', 'data-ciudad', '');
            setValOr('editarDireccion', 'data-direccion', '');
            setValOr('editarObservacion', 'data-observacion', '');
            setValOr('editarCarnetCi', 'data-carnet-ci', '');
            setValOr('editarCarnetComplemento', 'data-carnet-complemento', '');
            setValOr('editarFechaNacimiento', 'data-fecha-nacimiento', '');
            setValOr('editarRazon', 'data-razon', '');
            const formEl = document.getElementById('formEditarSocio');
            if (formEl) formEl.action = `/socios/${id}/editar/`;
        });
    });
});
