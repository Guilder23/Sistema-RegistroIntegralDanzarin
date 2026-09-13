document.addEventListener('DOMContentLoaded', function () {
	const filtrosForm = document.getElementById('asociacionesFiltrosForm');
	const busqueda = document.getElementById('inputAsociacionBusqueda');
	const estadoFiltro = document.getElementById('selectAsociacionActivo');
	let filtroTimer;
	const enviarFiltros = function () {
		if (filtrosForm) filtrosForm.submit();
	};
	if (busqueda) {
		busqueda.addEventListener('input', function () {
			clearTimeout(filtroTimer);
			filtroTimer = setTimeout(enviarFiltros, 300);
		});
	}
	if (estadoFiltro) estadoFiltro.addEventListener('change', enviarFiltros);

});
