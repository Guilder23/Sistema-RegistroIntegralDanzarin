document.addEventListener('DOMContentLoaded', function () {
	document.querySelectorAll('.btn-ver-admin').forEach(function (button) {
		button.addEventListener('click', function () {
			document.getElementById('verAdminUsername').textContent = button.dataset.username || '';
			document.getElementById('verAdminNombre').textContent = button.dataset.fullname || '';
			document.getElementById('verAdminEmail').textContent = button.dataset.email || '';
			document.getElementById('verAdminRol').textContent = button.dataset.rol || '';
			document.getElementById('verAdminAmbito').textContent = button.dataset.ambito || 'Global';
		});
	});
});
