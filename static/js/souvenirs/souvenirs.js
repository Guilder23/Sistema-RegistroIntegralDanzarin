document.addEventListener('DOMContentLoaded', function () {
    const configurarDependencias = function (tipo, asociacion, conjunto, evento) {
        const conjuntoGrupo = conjunto?.closest('.form-group');
        const actualizar = function () {
            const conjuntoActivo = tipo ? tipo.value === 'conjunto' : Boolean(conjunto);
            if (conjunto) {
                conjunto.required = conjuntoActivo;
                conjunto.disabled = !conjuntoActivo;
                if (conjuntoGrupo) conjuntoGrupo.style.display = conjuntoActivo ? '' : 'none';
                Array.from(conjunto.options).forEach(option => {
                    const visible = !option.value || !asociacion || !asociacion.value || option.dataset.asociacionId === asociacion.value;
                    option.hidden = !visible;
                    option.disabled = !visible;
                });
                if (!conjuntoActivo) conjunto.value = '';
            }
            if (evento) {
                Array.from(evento.options).forEach(option => {
                    const asociacionValida = !option.value || !asociacion || !asociacion.value || option.dataset.asociacionId === asociacion.value;
                    const conjuntoValido = !option.value || !conjunto
                        || (conjunto.value
                            ? (!option.dataset.conjuntoId || option.dataset.conjuntoId === conjunto.value)
                            : !option.dataset.conjuntoId);
                    option.hidden = !(asociacionValida && conjuntoValido);
                    option.disabled = option.hidden;
                });
            }
        };
        tipo?.addEventListener('change', actualizar);
        asociacion?.addEventListener('change', actualizar);
        conjunto?.addEventListener('change', actualizar);
        actualizar();
        return actualizar;
    };

    configurarDependencias(
        document.getElementById('crearSouvenirTipo'),
        document.getElementById('crearSouvenirAsociacion'),
        document.getElementById('crearSouvenirConjunto'),
        document.getElementById('crearSouvenirEvento')
    );
    const actualizarEditar = configurarDependencias(
        document.getElementById('editarSouvenirTipo'),
        document.getElementById('editarSouvenirAsociacion'),
        document.getElementById('editarSouvenirConjunto'),
        document.getElementById('editarSouvenirEvento')
    );

    const modalVer = document.getElementById('modalVerSouvenir');
    const modalEditarForm = document.getElementById('formEditarSouvenir');
    const modalEliminarForm = document.getElementById('formEliminarSouvenir');

    const populateVerModal = function(button) {
        if (!button) return;

        const nombre = button.getAttribute('data-nombre') || '';
        const evento = button.getAttribute('data-evento-nombre') || '-';
        const asociacion = button.getAttribute('data-asociacion') || '-';
        const conjunto = button.getAttribute('data-conjunto') || 'Toda la asociación';
        const creadoPor = button.getAttribute('data-creado-por') || 'No disponible';
        const descripcion = button.getAttribute('data-descripcion') || '';
        const stock = button.getAttribute('data-stock') || '0';
        const activo = button.getAttribute('data-activo') || 'No';
        const creado = button.getAttribute('data-creado') || '-';
        const imagenUrl = button.getAttribute('data-imagen') || null;

        const nombreEl = document.getElementById('verSouvenirNombre');
        const eventoEl = document.getElementById('verSouvenirEvento');
        const asociacionEl = document.getElementById('verSouvenirAsociacion');
        const conjuntoEl = document.getElementById('verSouvenirConjunto');
        const creadoPorEl = document.getElementById('verSouvenirCreadoPor');
        const descripcionEl = document.getElementById('verSouvenirDescripcion');
        const stockEl = document.getElementById('verSouvenirStock');
        const activoEl = document.getElementById('verSouvenirActivo');
        const creadoEl = document.getElementById('verSouvenirCreado');
        const imagenEl = document.getElementById('verSouvenirImagen');
        const imagenPlaceholder = document.getElementById('verSouvenirImagenPlaceholder');

        if (nombreEl) nombreEl.textContent = nombre;
        if (eventoEl) eventoEl.textContent = evento || '-';
        if (asociacionEl) asociacionEl.textContent = asociacion;
        if (conjuntoEl) conjuntoEl.textContent = conjunto;
        if (creadoPorEl) creadoPorEl.textContent = creadoPor;
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
            const asociacionId = button.getAttribute('data-asociacion-id') || '';
            const conjuntoId = button.getAttribute('data-conjunto-id') || '';
            const stock = button.getAttribute('data-stock') || '0';

            if (modalEditarForm) {
                modalEditarForm.action = `/souvenirs/gestion/${id}/editar/`;
            }

            const nombreInput = document.getElementById('editarSouvenirNombre');
            const descripcionInput = document.getElementById('editarSouvenirDescripcion');
            const eventoInput = document.getElementById('editarSouvenirEvento');
            const stockInput = document.getElementById('editarSouvenirStock');
            const asociacionInput = document.getElementById('editarSouvenirAsociacion');
            const conjuntoInput = document.getElementById('editarSouvenirConjunto');

            if (nombreInput) nombreInput.value = nombre;
            if (descripcionInput) descripcionInput.value = descripcion;
            if (eventoInput) eventoInput.value = eventoId;
            if (stockInput) stockInput.value = stock;
            if (asociacionInput) asociacionInput.value = asociacionId;
            if (conjuntoInput) conjuntoInput.value = conjuntoId;
            const tipoInput = document.getElementById('editarSouvenirTipo');
            if (tipoInput) tipoInput.value = button.getAttribute('data-tipo-ambito') || 'asociacion';
            if (actualizarEditar) actualizarEditar();
            if (conjuntoInput) conjuntoInput.value = conjuntoId;
        });
    });

    const filtrosForm = document.getElementById('souvenirsFiltrosForm');
    const searchInput = document.getElementById('inputSouvenirBusqueda');
    const activoSelect = document.getElementById('selectSouvenirActivo');
    const eventoSelect = document.getElementById('selectSouvenirEvento');
    const asociacionSelect = document.getElementById('selectSouvenirAsociacion');
    const conjuntoSelect = document.getElementById('selectSouvenirConjunto');
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
    if (asociacionSelect) asociacionSelect.addEventListener('change', submitFiltros);
    if (conjuntoSelect) conjuntoSelect.addEventListener('change', submitFiltros);

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
