document.addEventListener('DOMContentLoaded', function () {
	const role = document.getElementById('editarAdminRol');
	const group = document.getElementById('editarAdminAsociacion');
	const subgroup = document.getElementById('editarAdminConjunto');

	const updateScope = function () {
		if (!role || !group || !subgroup) return;
		const requiresGroup = role.value === 'administrador_asociacion' || role.value === 'administrador_conjunto';
		const requiresSubgroup = role.value === 'administrador_conjunto';
		group.disabled = !requiresGroup;
		group.required = requiresGroup;
		subgroup.disabled = !requiresSubgroup;
		subgroup.required = requiresSubgroup;
		Array.from(subgroup.options).forEach(function (option) {
			if (!option.dataset.asociacionId) return;
			option.hidden = !requiresSubgroup || option.dataset.asociacionId !== group.value;
		});
	};

	role?.addEventListener('change', updateScope);
	group?.addEventListener('change', updateScope);
	document.querySelectorAll('.btn-editar-admin').forEach(function (button) {
		button.addEventListener('click', function () {
			document.getElementById('formEditarAdmin').action = '/danzarines/admins/' + button.dataset.id + '/editar/';
			document.getElementById('editarAdminUsername').value = button.dataset.username || '';
			document.getElementById('editarAdminFirstName').value = button.dataset.firstName || '';
			document.getElementById('editarAdminLastName').value = button.dataset.lastName || '';
			document.getElementById('editarAdminEmail').value = button.dataset.email || '';
			if (role) role.value = button.dataset.rol || 'administrador_asociacion';
			if (group) group.value = button.dataset.asociacion || '';
			if (subgroup) subgroup.value = button.dataset.conjunto || '';
			updateScope();
		});
	});
});
