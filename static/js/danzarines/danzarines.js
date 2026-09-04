document.addEventListener('DOMContentLoaded', function () {
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

});
