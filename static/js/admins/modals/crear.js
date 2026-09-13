document.addEventListener('DOMContentLoaded', function () {
	const role = document.getElementById('crearAdminRol');
	const group = document.getElementById('crearAdminAsociacion');
	const subgroup = document.getElementById('crearAdminConjunto');
	if (!role || !group || !subgroup) return;

	const updateScope = function () {
		const requiresGroup = role.value === 'administrador_asociacion' || role.value === 'administrador_conjunto';
		const requiresSubgroup = role.value === 'administrador_conjunto';
		group.disabled = !requiresGroup;
		group.required = requiresGroup;
		subgroup.disabled = !requiresSubgroup;
		subgroup.required = requiresSubgroup;
		if (!requiresGroup) group.value = '';
		if (!requiresSubgroup) subgroup.value = '';
		Array.from(subgroup.options).forEach(function (option) {
			if (!option.dataset.asociacionId) return;
			option.hidden = !requiresSubgroup || option.dataset.asociacionId !== group.value;
		});
		if (requiresSubgroup && subgroup.selectedOptions[0]?.hidden) subgroup.value = '';
	};

	role.addEventListener('change', updateScope);
	group.addEventListener('change', updateScope);
	updateScope();
});
