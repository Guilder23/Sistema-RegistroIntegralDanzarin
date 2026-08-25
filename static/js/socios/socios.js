document.addEventListener('DOMContentLoaded', function () {
    const sociosForm = document.getElementById('sociosFiltrosForm');
    const searchInput = document.getElementById('inputSocioBusqueda');
    const estadoSelect = document.getElementById('selectSocioEstado');
    let debounceTimer = null;

    const submitFiltros = function () {
        if (sociosForm) {
            sociosForm.submit();
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
