document.addEventListener('DOMContentLoaded', function () {
    const filtroBusqueda = document.getElementById('filtroBusqueda');
    const filtroEstado = document.getElementById('filtroEstado');
    const filtroSouvenir = document.getElementById('filtroSouvenir');
    const filtroSouvenirId = document.getElementById('filtroSouvenirId');
    const filtroOrden = document.getElementById('filtroOrden');
    const filtroDesde = document.getElementById('filtroDesde');
    const filtroHasta = document.getElementById('filtroHasta');
    const btnLimpiarFiltros = document.getElementById('btnLimpiarFiltros');

    const aplicarFiltros = () => {
        const params = new URLSearchParams();
        if (filtroBusqueda.value.trim()) {
            params.set('q', filtroBusqueda.value.trim());
        }
        if (filtroEstado.value) {
            params.set('estado', filtroEstado.value);
        }
        if (filtroSouvenir.value) {
            params.set('recibio_souvenir', filtroSouvenir.value);
        }
        if (filtroSouvenirId.value) {
            params.set('souvenir_id', filtroSouvenirId.value);
        }
        if (filtroOrden.value) {
            params.set('orden', filtroOrden.value);
        }
        if (filtroDesde.value) {
            params.set('desde', filtroDesde.value);
        }
        if (filtroHasta.value) {
            params.set('hasta', filtroHasta.value);
        }
        const nuevaUrl = `${window.location.pathname}?${params.toString()}`;
        window.history.replaceState({}, '', nuevaUrl);
        window.location.search = params.toString();
    };

    const debounce = (fn, delay = 400) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn(...args), delay);
        };
    };

    filtroBusqueda.addEventListener('input', debounce(aplicarFiltros));
    filtroEstado.addEventListener('change', aplicarFiltros);
    filtroSouvenir.addEventListener('change', aplicarFiltros);
    filtroSouvenirId.addEventListener('change', aplicarFiltros);
    filtroOrden.addEventListener('change', aplicarFiltros);
    filtroDesde.addEventListener('change', aplicarFiltros);
    filtroHasta.addEventListener('change', aplicarFiltros);
    btnLimpiarFiltros.addEventListener('click', () => {
        filtroBusqueda.value = '';
        filtroEstado.value = '';
        filtroCiudad.value = '';
        filtroSouvenir.value = '';
        filtroSouvenirId.value = '';
        filtroOrden.value = 'recientes';
        filtroDesde.value = '';
        filtroHasta.value = '';
        window.location.href = window.location.pathname;
    });
});
