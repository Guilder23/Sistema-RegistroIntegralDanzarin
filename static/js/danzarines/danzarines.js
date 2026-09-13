document.addEventListener('DOMContentLoaded', function () {
    const crearForm = document.getElementById('formCrearDanzarin');
    const danzarinesForm = document.getElementById('danzarinesFiltrosForm');
    const searchInput = document.getElementById('inputDanzarinBusqueda');
    const estadoSelect = document.getElementById('selectDanzarinEstado');
    const asociacionSelect = document.getElementById('selectDanzarinAsociacion');
    const conjuntoSelect = document.getElementById('selectDanzarinConjunto');
    const bloqueSelect = document.getElementById('selectDanzarinBloque');
    let debounceTimer = null;

    const submitFiltros = function () {
        if (danzarinesForm) {
            danzarinesForm.submit();
        }
    };

    const scheduleSubmit = function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(submitFiltros, 300);
    };

    if (searchInput) {
        searchInput.addEventListener('input', scheduleSubmit);
    }

    if (estadoSelect) {
        estadoSelect.addEventListener('change', scheduleSubmit);
    }

    const filtrarOpciones = function (select, attribute, value) {
        if (!select) return;
        Array.from(select.options).forEach(function (option) {
            const visible = !option.value || option.dataset[attribute] === value;
            option.hidden = !visible;
            option.disabled = !visible;
        });
        if (select.selectedOptions[0]?.disabled) select.value = '';
    };

    const actualizarConjuntos = function () {
        filtrarOpciones(conjuntoSelect, 'asociacionId', asociacionSelect?.value || '');
        actualizarBloques();
    };

    const actualizarBloques = function () {
        filtrarOpciones(bloqueSelect, 'conjuntoId', conjuntoSelect?.value || '');
    };

    asociacionSelect?.addEventListener('change', function () {
        actualizarConjuntos();
        scheduleSubmit();
    });
    conjuntoSelect?.addEventListener('change', function () {
        actualizarBloques();
        scheduleSubmit();
    });
    bloqueSelect?.addEventListener('change', scheduleSubmit);
    actualizarConjuntos();

    const camposObligatorios = crearForm ? Array.from(crearForm.querySelectorAll('[required]')) : [];
    const camposNumericos = crearForm ? crearForm.querySelectorAll('.numeric-only') : [];
    const limpiarError = function (campo) {
        campo.classList.remove('field-invalid');
        const error = campo.parentElement.querySelector('.form-field-error');
        if (error) error.remove();
    };
    const mostrarError = function (campo, mensaje) {
        limpiarError(campo);
        campo.classList.add('field-invalid');
        const error = document.createElement('small');
        error.className = 'form-field-error';
        error.textContent = mensaje;
        campo.parentElement.appendChild(error);
    };

    camposObligatorios.forEach(function (campo) {
        campo.addEventListener('input', function () { limpiarError(campo); });
        campo.addEventListener('change', function () { limpiarError(campo); });
        campo.addEventListener('keydown', function (event) {
            if (event.key !== 'Enter' || campo.tagName === 'TEXTAREA') return;
            event.preventDefault();
            const indice = camposObligatorios.indexOf(campo);
            const siguiente = camposObligatorios[indice + 1];
            if (siguiente) {
                siguiente.focus();
            } else if (crearForm) {
                crearForm.requestSubmit();
            }
        });
    });

    camposNumericos.forEach(function (campo) {
        campo.addEventListener('input', function () {
            const valorNumerico = campo.value.replace(/\D/g, '');
            if (campo.value !== valorNumerico) campo.value = valorNumerico;
        });
        campo.addEventListener('keydown', function (event) {
            const teclasPermitidas = ['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight', 'Home', 'End'];
            if (teclasPermitidas.includes(event.key) || event.ctrlKey || event.metaKey) return;
            if (!/^[0-9]$/.test(event.key)) event.preventDefault();
        });
    });

    crearForm?.addEventListener('submit', function (event) {
        let primerCampoInvalido = null;
        camposObligatorios.forEach(function (campo) {
            if (campo.disabled || campo.value.trim()) {
                limpiarError(campo);
                return;
            }
            mostrarError(campo, 'Completa este campo obligatorio.');
            primerCampoInvalido ||= campo;
        });
        if (primerCampoInvalido) {
            event.preventDefault();
            primerCampoInvalido.focus();
        }
    });

});
