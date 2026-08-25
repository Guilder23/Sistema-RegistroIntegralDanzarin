document.addEventListener('DOMContentLoaded', function () {
    const modalVer = document.getElementById('modalVerEvento');
    const modalEditarForm = document.getElementById('formEditarEvento');
    const modalEliminarForm = document.getElementById('formEliminarEvento');

    const populateVerModal = function(button) {
        if (!button) return;
        const nombre = button.getAttribute('data-nombre') || '';
        const descripcion = button.getAttribute('data-descripcion') || '';
        const fecha = button.getAttribute('data-fecha') || '-';
        const lugar = button.getAttribute('data-lugar') || '-';
        const activo = button.getAttribute('data-activo') || 'No';
        const creado = button.getAttribute('data-creado') || '-';

        const nombreEl = document.getElementById('verEventoNombre');
        const descripcionEl = document.getElementById('verEventoDescripcion');
        const fechaEl = document.getElementById('verEventoFecha');
        const lugarEl = document.getElementById('verEventoLugar');
        const activoEl = document.getElementById('verEventoActivo');
        const creadoEl = document.getElementById('verEventoCreado');

        if (nombreEl) nombreEl.textContent = nombre;
        if (descripcionEl) descripcionEl.textContent = descripcion || 'No disponible';
        if (fechaEl) fechaEl.textContent = fecha;
        if (lugarEl) lugarEl.textContent = lugar || '-';
        if (activoEl) activoEl.textContent = activo;
        if (creadoEl) creadoEl.textContent = creado;
    };

    if (modalVer) {
        const verButtons = document.querySelectorAll('.btn-ver-evento');
        verButtons.forEach(button => {
            button.addEventListener('click', function () {
                populateVerModal(button);
            });
        });
    }

    const editarButtons = document.querySelectorAll('.btn-editar-evento');
    editarButtons.forEach(button => {
        button.addEventListener('click', function () {
            const id = button.getAttribute('data-id');
            const nombre = button.getAttribute('data-nombre') || '';
            const descripcion = button.getAttribute('data-descripcion') || '';
            const fecha = button.getAttribute('data-fecha') || '';
            const lugar = button.getAttribute('data-lugar') || '';
            const activo = button.getAttribute('data-activo') === 'true';

            if (modalEditarForm) {
                modalEditarForm.action = `/eventos/${id}/editar/`;
            }

            const nombreInput = document.getElementById('editarEventoNombre');
            const descripcionInput = document.getElementById('editarEventoDescripcion');
            const fechaInput = document.getElementById('editarEventoFecha');
            const lugarInput = document.getElementById('editarEventoLugar');
            const activoInput = document.getElementById('editarEventoActivo');

            if (nombreInput) nombreInput.value = nombre;
            if (descripcionInput) descripcionInput.value = descripcion;
            if (fechaInput) fechaInput.value = fecha;
            if (lugarInput) lugarInput.value = lugar;
            if (activoInput) activoInput.checked = activo;
        });
    });

    const filtrosForm = document.getElementById('eventosFiltrosForm');
    const searchInput = document.getElementById('inputEventoBusqueda');
    const activoSelect = document.getElementById('selectEventoActivo');
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

    const eliminarButtons = document.querySelectorAll('.btn-eliminar-evento');
    eliminarButtons.forEach(button => {
        button.addEventListener('click', function () {
            const id = button.getAttribute('data-id');
            const nombre = button.getAttribute('data-nombre') || '';

            if (modalEliminarForm) {
                modalEliminarForm.action = `/eventos/${id}/eliminar/`;
            }

            const nombreEl = document.getElementById('eliminarEventoNombre');
            if (nombreEl) nombreEl.textContent = nombre;
        });
    });
});
