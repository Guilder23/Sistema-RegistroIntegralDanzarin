document.addEventListener('DOMContentLoaded', function () {
    const modalVer = document.getElementById('modalVerEvento');
    const modalEditarForm = document.getElementById('formEditarEvento');
    const modalEliminarForm = document.getElementById('formEliminarEvento');

    const configurarAmbito = function (tipoSelect, asociacionSelect, conjuntoSelect, conjuntoGrupo) {
        if (!tipoSelect || !asociacionSelect || !conjuntoSelect || !conjuntoGrupo) return;

        const actualizar = function () {
            const esConjunto = tipoSelect.value === 'conjunto';
            conjuntoGrupo.style.display = esConjunto ? '' : 'none';
            conjuntoSelect.required = esConjunto;
            Array.from(conjuntoSelect.options).forEach(function (option) {
                const esOpcionValida = !option.value || option.getAttribute('data-asociacion-id') === asociacionSelect.value;
                option.hidden = !esOpcionValida;
                if (!esOpcionValida && option.selected) conjuntoSelect.value = '';
            });
            if (!esConjunto) conjuntoSelect.value = '';
        };

        tipoSelect.addEventListener('change', actualizar);
        asociacionSelect.addEventListener('change', actualizar);
        actualizar();
        return actualizar;
    };

    const crearAmbito = configurarAmbito(
        document.getElementById('crearEventoTipoAmbito'),
        document.getElementById('crearEventoAsociacion'),
        document.getElementById('crearEventoConjunto'),
        document.getElementById('crearEventoConjuntoGrupo')
    );
    const editarTipoAmbito = document.getElementById('editarEventoTipoAmbito');
    const editarAsociacion = document.getElementById('editarEventoAsociacion');
    const editarConjunto = document.getElementById('editarEventoConjunto');
    const editarConjuntoGrupo = document.getElementById('editarEventoConjuntoGrupo');
    const actualizarAmbitoEditar = configurarAmbito(
        editarTipoAmbito,
        editarAsociacion,
        editarConjunto,
        editarConjuntoGrupo
    );

    const populateVerModal = function(button) {
        if (!button) return;
        const nombre = button.getAttribute('data-nombre') || '';
        const descripcion = button.getAttribute('data-descripcion') || '';
        const fecha = button.getAttribute('data-fecha') || '-';
        const lugar = button.getAttribute('data-lugar') || '-';
        const tipoAmbito = button.getAttribute('data-tipo-ambito') || 'asociacion';
        const asociacionNombre = button.getAttribute('data-asociacion-nombre') || '-';
        const conjuntoNombre = button.getAttribute('data-conjunto-nombre') || '';
        const activo = button.getAttribute('data-activo') || 'No';
        const creadoPor = button.getAttribute('data-creado-por') || 'No disponible';
        const creado = button.getAttribute('data-creado') || '-';

        const nombreEl = document.getElementById('verEventoNombre');
        const descripcionEl = document.getElementById('verEventoDescripcion');
        const fechaEl = document.getElementById('verEventoFecha');
        const lugarEl = document.getElementById('verEventoLugar');
        const ambitoEl = document.getElementById('verEventoAmbito');
        const activoEl = document.getElementById('verEventoActivo');
        const creadoPorEl = document.getElementById('verEventoCreadoPor');
        const creadoEl = document.getElementById('verEventoCreado');

        if (nombreEl) nombreEl.textContent = nombre;
        if (descripcionEl) descripcionEl.textContent = descripcion || 'No disponible';
        if (fechaEl) fechaEl.textContent = fecha;
        if (lugarEl) lugarEl.textContent = lugar || '-';
        if (ambitoEl) ambitoEl.textContent = tipoAmbito === 'conjunto'
            ? `Conjunto: ${conjuntoNombre} (${asociacionNombre})`
            : `Asociación: ${asociacionNombre}`;
        if (activoEl) activoEl.textContent = activo;
        if (creadoPorEl) creadoPorEl.textContent = creadoPor;
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
            const tipoAmbito = button.getAttribute('data-tipo-ambito') || 'asociacion';
            const asociacionId = button.getAttribute('data-asociacion-id') || '';
            const conjuntoId = button.getAttribute('data-conjunto-id') || '';
            const activo = button.getAttribute('data-activo') === 'true';

            if (modalEditarForm) {
                modalEditarForm.action = `/eventos/${id}/editar/`;
            }

            const nombreInput = document.getElementById('editarEventoNombre');
            const descripcionInput = document.getElementById('editarEventoDescripcion');
            const fechaInput = document.getElementById('editarEventoFecha');
            const lugarInput = document.getElementById('editarEventoLugar');
            const activoInput = document.getElementById('editarEventoActivo');

            if (editarTipoAmbito) editarTipoAmbito.value = tipoAmbito;
            if (editarAsociacion) editarAsociacion.value = asociacionId;
            if (editarConjunto) editarConjunto.value = conjuntoId;
            if (actualizarAmbitoEditar) actualizarAmbitoEditar();
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
