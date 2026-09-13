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

	document.querySelectorAll('[data-target="#modalEditarAsociacion"]').forEach(function (button) {
		button.addEventListener('click', function () {
			document.getElementById('formEditarAsociacion').action = '/asociaciones/' + button.dataset.id + '/editar/';
			document.getElementById('editarAsociacionNombre').value = button.dataset.nombre;
			document.getElementById('editarAsociacionActivo').checked = button.dataset.activo === '1';
		});
	});
	document.querySelectorAll('[data-target="#modalVerAsociacion"]').forEach(function (button) {
		button.addEventListener('click', function () {
			document.getElementById('verAsociacionNombre').textContent = button.dataset.nombre;
			document.getElementById('verAsociacionConjuntos').textContent = button.dataset.conjuntos;
			document.getElementById('verAsociacionIntegrantes').textContent = button.dataset.integrantes;
		});
	});
	const eliminarForm = document.getElementById('formEliminarAsociacion');
	document.querySelectorAll('.btn-eliminar-asociacion').forEach(function (button) {
		button.addEventListener('click', function () {
			eliminarForm.action = '/asociaciones/' + button.dataset.id + '/eliminar/';
			document.getElementById('eliminarAsociacionNombre').textContent = button.dataset.nombre;
		});
	});
});
