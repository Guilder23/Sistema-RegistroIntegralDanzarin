// JS para admins

function setupAdminModals() {
    const filtrosForm = document.getElementById('adminsFiltrosForm');
    const searchInput = document.getElementById('inputAdminBusqueda');
    const activoSelect = document.getElementById('selectAdminActivo');
    let debounceTimer = null;

    const submitFiltros = function () {
        if (filtrosForm) {
            filtrosForm.submit();
        }
    };

    const scheduleSubmit = function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(submitFiltros, 300);
    };

    if (searchInput) {
        searchInput.addEventListener('input', scheduleSubmit);
    }

    if (activoSelect) {
        activoSelect.addEventListener('change', scheduleSubmit);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAdminModals);
} else {
    setupAdminModals();
}
