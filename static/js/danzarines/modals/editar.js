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
    const formEditar = document.getElementById('formEditarDanzarin');

    modalEditar.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const id = button.getAttribute('data-id');
        const setVal = (idName, val) => { const el = document.getElementById(idName); if (!el) return; el.value = val; };
        const setValOr = (idName, attrName, fallback='') => setVal(idName, button.getAttribute(attrName) || fallback);
        const codigo = button.getAttribute('data-codigo-danzarin') || '';
        setVal('editarCodigoPrefijo', codigo.slice(0, 2));
        setVal('editarCodigoNumero', codigo.slice(2));
        setValOr('editarNombre', 'data-nombre', '');
        setValOr('editarApellidoPaterno', 'data-apellido-paterno', '');
        setValOr('editarApellidoMaterno', 'data-apellido-materno', '');
        setValOr('editarEmail', 'data-email', '');
        setValOr('editarSexo', 'data-sexo', '');
        setValOr('editarTelefono', 'data-telefono', '');
        setValOr('editarCiudad', 'data-ciudad', '');
        setValOr('editarDireccion', 'data-direccion', '');
        setValOr('editarObservacion', 'data-observacion', '');
        setValOr('editarCarnetCi', 'data-carnet-ci', '');
        setValOr('editarCarnetComplemento', 'data-carnet-complemento', '');
        setValOr('editarFechaNacimiento', 'data-fecha-nacimiento', '');
        setValOr('editarFechaIngresoGrupo', 'data-fecha-ingreso-grupo', '');
        setValOr('editarAntiguedadObservacion', 'data-antiguedad-observacion', '');
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
            const codigo = button.getAttribute('data-codigo-danzarin') || '';
            setVal('editarCodigoPrefijo', codigo.slice(0, 2));
            setVal('editarCodigoNumero', codigo.slice(2));
            setValOr('editarNombre', 'data-nombre', '');
            setValOr('editarApellidoPaterno', 'data-apellido-paterno', '');
            setValOr('editarApellidoMaterno', 'data-apellido-materno', '');
            setValOr('editarEmail', 'data-email', '');
            setValOr('editarSexo', 'data-sexo', '');
            setValOr('editarTelefono', 'data-telefono', '');
            setValOr('editarCiudad', 'data-ciudad', '');
            setValOr('editarDireccion', 'data-direccion', '');
            setValOr('editarObservacion', 'data-observacion', '');
            setValOr('editarCarnetCi', 'data-carnet-ci', '');
            setValOr('editarCarnetComplemento', 'data-carnet-complemento', '');
            setValOr('editarFechaNacimiento', 'data-fecha-nacimiento', '');
            setValOr('editarFechaIngresoGrupo', 'data-fecha-ingreso-grupo', '');
            setValOr('editarAntiguedadObservacion', 'data-antiguedad-observacion', '');
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

    const camposObligatorios = formEditar ? Array.from(formEditar.querySelectorAll('[required]')) : [];
    const limpiarError = function (campo) {
        campo.classList.remove('field-invalid');
        campo.parentElement.querySelector('.form-field-error')?.remove();
    };
    const mostrarError = function (campo) {
        limpiarError(campo);
        campo.classList.add('field-invalid');
        const error = document.createElement('small');
        error.className = 'form-field-error';
        error.textContent = 'Completa este campo obligatorio.';
        campo.parentElement.appendChild(error);
    };
    camposObligatorios.forEach(function (campo) {
        campo.addEventListener('input', function () { limpiarError(campo); });
        campo.addEventListener('change', function () { limpiarError(campo); });
        campo.addEventListener('keydown', function (event) {
            if (event.key !== 'Enter' || campo.tagName === 'TEXTAREA') return;
            event.preventDefault();
            const siguiente = camposObligatorios[camposObligatorios.indexOf(campo) + 1];
            if (siguiente) siguiente.focus();
            else formEditar?.requestSubmit();
        });
    });
    formEditar?.querySelectorAll('.numeric-only').forEach(function (campo) {
        campo.addEventListener('input', function () {
            campo.value = campo.value.replace(/\D/g, '');
        });
    });
    formEditar?.addEventListener('submit', function (event) {
        let primerCampoInvalido = null;
        camposObligatorios.forEach(function (campo) {
            if (campo.disabled || campo.value.trim()) limpiarError(campo);
            else {
                mostrarError(campo);
                primerCampoInvalido ||= campo;
            }
        });
        if (primerCampoInvalido) {
            event.preventDefault();
            primerCampoInvalido.focus();
        }
    });
});
