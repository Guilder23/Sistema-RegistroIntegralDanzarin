document.addEventListener('DOMContentLoaded', function () {
	const filtrosForm = document.getElementById('conjuntosFiltrosForm');
	const busqueda = document.getElementById('inputConjuntoBusqueda');
	const asociacionFiltro = document.getElementById('selectConjuntoAsociacion');
	const estadoFiltro = document.getElementById('selectConjuntoActivo');
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
	[asociacionFiltro, estadoFiltro].forEach(function (select) {
		if (select) select.addEventListener('change', enviarFiltros);
	});

});
