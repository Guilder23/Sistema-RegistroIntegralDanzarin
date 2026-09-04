document.addEventListener('DOMContentLoaded', function () {
    const danzarinesForm = document.getElementById('danzarinesFiltrosForm');
    const searchInput = document.getElementById('inputDanzarinBusqueda');
    const estadoSelect = document.getElementById('selectDanzarinEstado');
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
});
