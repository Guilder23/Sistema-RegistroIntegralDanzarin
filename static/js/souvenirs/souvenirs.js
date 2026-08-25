document.addEventListener('DOMContentLoaded', function () {
    const modalVer = document.getElementById('modalVerSouvenir');
    const modalEditarForm = document.getElementById('formEditarSouvenir');
    const modalEliminarForm = document.getElementById('formEliminarSouvenir');

    const populateVerModal = function(button) {
        if (!button) return;

        const nombre = button.getAttribute('data-nombre') || '';
        const evento = button.getAttribute('data-evento-nombre') || '-';
        const descripcion = button.getAttribute('data-descripcion') || '';
        const stock = button.getAttribute('data-stock') || '0';
        const activo = button.getAttribute('data-activo') || 'No';
        const creado = button.getAttribute('data-creado') || '-';
        const imagenUrl = button.getAttribute('data-imagen') || null;

        const nombreEl = document.getElementById('verSouvenirNombre');
        const eventoEl = document.getElementById('verSouvenirEvento');
        const descripcionEl = document.getElementById('verSouvenirDescripcion');
        const stockEl = document.getElementById('verSouvenirStock');
        const activoEl = document.getElementById('verSouvenirActivo');
        const creadoEl = document.getElementById('verSouvenirCreado');
        const imagenEl = document.getElementById('verSouvenirImagen');
        const imagenPlaceholder = document.getElementById('verSouvenirImagenPlaceholder');

        if (nombreEl) nombreEl.textContent = nombre;
        if (eventoEl) eventoEl.textContent = evento || '-';
        if (descripcionEl) descripcionEl.textContent = descripcion || 'No disponible';
        if (stockEl) stockEl.textContent = stock;
        if (activoEl) activoEl.textContent = activo;
        if (creadoEl) creadoEl.textContent = creado;

        if (imagenUrl && imagenEl) {
            imagenEl.src = imagenUrl;
            imagenEl.style.display = 'block';
            if (imagenPlaceholder) imagenPlaceholder.style.display = 'none';
        } else {
            if (imagenEl) imagenEl.style.display = 'none';
            if (imagenPlaceholder) imagenPlaceholder.style.display = 'block';
        }
    };

    if (modalVer) {
        const verButtons = document.querySelectorAll('.btn-ver-souvenir');
        verButtons.forEach(button => {
            button.addEventListener('click', function () {
                populateVerModal(button);
            });
        });
    }

    const editarButtons = document.querySelectorAll('.btn-editar-souvenir');
    editarButtons.forEach(button => {
        button.addEventListener('click', function () {
            const id = button.getAttribute('data-id');
            const nombre = button.getAttribute('data-nombre') || '';
            const descripcion = button.getAttribute('data-descripcion') || '';
            const eventoId = button.getAttribute('data-evento-id') || '';
            const stock = button.getAttribute('data-stock') || '0';

            if (modalEditarForm) {
                modalEditarForm.action = `/souvenirs/gestion/${id}/editar/`;
            }

            const nombreInput = document.getElementById('editarSouvenirNombre');
            const descripcionInput = document.getElementById('editarSouvenirDescripcion');
            const eventoInput = document.getElementById('editarSouvenirEvento');
            const stockInput = document.getElementById('editarSouvenirStock');

            if (nombreInput) nombreInput.value = nombre;
            if (descripcionInput) descripcionInput.value = descripcion;
            if (eventoInput) eventoInput.value = eventoId;
            if (stockInput) stockInput.value = stock;
        });
    });

    const filtrosForm = document.getElementById('souvenirsFiltrosForm');
    const searchInput = document.getElementById('inputSouvenirBusqueda');
    const activoSelect = document.getElementById('selectSouvenirActivo');
    const eventoSelect = document.getElementById('selectSouvenirEvento');
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
        activoSelect.addEventListener('change', submitFiltros);
    }

    if (eventoSelect) {
        eventoSelect.addEventListener('change', submitFiltros);
    }

    const eliminarButtons = document.querySelectorAll('.btn-eliminar-souvenir');
    eliminarButtons.forEach(button => {
        button.addEventListener('click', function () {
            const id = button.getAttribute('data-id');
            const nombre = button.getAttribute('data-nombre') || '';

            if (modalEliminarForm) {
                modalEliminarForm.action = `/souvenirs/gestion/${id}/eliminar/`;
            }

            const nombreEl = document.getElementById('eliminarSouvenirNombre');
            if (nombreEl) nombreEl.textContent = nombre;
        });
    });
});
