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

	document.querySelectorAll('[data-target="#modalEditarConjunto"]').forEach(function (button) {
		button.addEventListener('click', function () {
			document.getElementById('formEditarConjunto').action = '/conjuntos/' + button.dataset.id + '/editar/';
			document.getElementById('editarConjuntoNombre').value = button.dataset.nombre;
			document.getElementById('editarConjuntoActivo').checked = button.dataset.activo === '1';
		});
	});
	document.querySelectorAll('[data-target="#modalVerConjunto"]').forEach(function (button) {
		button.addEventListener('click', function () {
			document.getElementById('verConjuntoNombre').textContent = button.dataset.nombre;
			document.getElementById('verConjuntoAsociacion').textContent = button.dataset.asociacion;
		});
	});
	const eliminarForm = document.getElementById('formEliminarConjunto');
	document.querySelectorAll('.btn-eliminar-conjunto').forEach(function (button) {
		button.addEventListener('click', function () {
			eliminarForm.action = '/conjuntos/' + button.dataset.id + '/eliminar/';
			document.getElementById('eliminarConjuntoNombre').textContent = button.dataset.nombre;
		});
	});
});
