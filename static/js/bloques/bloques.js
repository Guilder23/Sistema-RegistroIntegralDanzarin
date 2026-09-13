document.addEventListener('DOMContentLoaded', function () {
    const filtrosForm = document.getElementById('bloquesFiltrosForm');
    const busqueda = document.getElementById('inputBloqueBusqueda');
    const asociacionFiltro = document.getElementById('selectBloqueAsociacion');
    const conjuntoFiltro = document.getElementById('selectBloqueConjunto');
    const estadoFiltro = document.getElementById('selectBloqueActivo');
    let filtroTimer;
    const enviarFiltros = function () { if (filtrosForm) filtrosForm.submit(); };
    if (busqueda) busqueda.addEventListener('input', function () {
        clearTimeout(filtroTimer);
        filtroTimer = setTimeout(enviarFiltros, 300);
    });
    [asociacionFiltro, conjuntoFiltro, estadoFiltro].forEach(function (select) {
        if (select) select.addEventListener('change', enviarFiltros);
    });
});
