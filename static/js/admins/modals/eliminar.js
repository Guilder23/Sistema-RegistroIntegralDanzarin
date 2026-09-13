document.addEventListener('DOMContentLoaded', function () {
	const form = document.getElementById('formEliminarAdmin');
	const modal = document.getElementById('modalEliminarAdmin');

	const cerrarModal = function () {
		if (!modal) return;
		modal.classList.remove('show');
		modal.style.display = 'none';
		modal.setAttribute('aria-hidden', 'true');
		document.body.classList.remove('modal-open');
		document.querySelectorAll('.modal-backdrop-admin').forEach(function (backdrop) {
			backdrop.remove();
		});
	};

	const abrirModal = function () {
		if (!modal) return;
		modal.classList.add('show');
		modal.style.display = 'block';
		modal.removeAttribute('aria-hidden');
		modal.setAttribute('aria-modal', 'true');
		document.body.classList.add('modal-open');

		const backdrop = document.createElement('div');
		backdrop.className = 'modal-backdrop fade show modal-backdrop-admin';
		backdrop.addEventListener('click', cerrarModal);
		document.body.appendChild(backdrop);
	};

	document.querySelectorAll('.btn-eliminar-admin').forEach(function (button) {
		button.addEventListener('click', function (event) {
			event.preventDefault();
			event.stopImmediatePropagation();
			if (form) form.action = '/danzarines/admins/' + button.dataset.id + '/eliminar/';
			const username = document.getElementById('eliminarAdminUsername');
			if (username) username.textContent = button.dataset.username || '';
			abrirModal();
		});
	});

	if (modal) {
		modal.querySelectorAll('[data-dismiss="modal"]').forEach(function (button) {
			button.addEventListener('click', cerrarModal);
		});
		modal.addEventListener('click', function (event) {
			if (event.target === modal) cerrarModal();
		});
	}
});
