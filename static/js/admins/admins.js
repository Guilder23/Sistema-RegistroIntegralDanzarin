// JS para admins

function setupAdminModals() {
    function configureScope(roleId, groupId, subgroupId) {
        const role = document.getElementById(roleId);
        const group = document.getElementById(groupId);
        const subgroup = document.getElementById(subgroupId);
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
    }

    configureScope('crearAdminRol', 'crearAdminAsociacion', 'crearAdminConjunto');
    configureScope('editarAdminRol', 'editarAdminAsociacion', 'editarAdminConjunto');

    const verButtons = document.querySelectorAll('.btn-ver-admin');
    const editarButtons = document.querySelectorAll('.btn-editar-admin');
    const eliminarButtons = document.querySelectorAll('.btn-eliminar-admin');

    verButtons.forEach(button => {
        button.addEventListener('click', () => {
            const username = button.getAttribute('data-username') || '';
            const fullname = button.getAttribute('data-fullname') || '';
            const email = button.getAttribute('data-email') || '';
            const rol = button.getAttribute('data-rol') || '';
            const ambito = button.getAttribute('data-ambito') || 'Global';
            const usernameEl = document.getElementById('verAdminUsername');
            const nombreEl = document.getElementById('verAdminNombre');
            const emailEl = document.getElementById('verAdminEmail');
            if (usernameEl) usernameEl.textContent = username;
            if (nombreEl) nombreEl.textContent = fullname;
            if (emailEl) emailEl.textContent = email;
            const rolEl = document.getElementById('verAdminRol');
            const ambitoEl = document.getElementById('verAdminAmbito');
            if (rolEl) rolEl.textContent = rol;
            if (ambitoEl) ambitoEl.textContent = ambito;
        });
    });

    editarButtons.forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');
            const username = button.getAttribute('data-username') || '';
            const firstName = button.getAttribute('data-first-name') || '';
            const lastName = button.getAttribute('data-last-name') || '';
            const email = button.getAttribute('data-email') || '';
            const rol = button.getAttribute('data-rol') || 'administrador_asociacion';
            const asociacion = button.getAttribute('data-asociacion') || '';
            const conjunto = button.getAttribute('data-conjunto') || '';
            const form = document.getElementById('formEditarAdmin');
            if (form) {
                form.action = `/socios/admins/${id}/editar/`;
            }
            const usernameEl = document.getElementById('editarAdminUsername');
            const firstNameEl = document.getElementById('editarAdminFirstName');
            const lastNameEl = document.getElementById('editarAdminLastName');
            const emailEl = document.getElementById('editarAdminEmail');
            if (usernameEl) usernameEl.value = username;
            if (firstNameEl) firstNameEl.value = firstName;
            if (lastNameEl) lastNameEl.value = lastName;
            if (emailEl) emailEl.value = email;
            const rolEl = document.getElementById('editarAdminRol');
            const asociacionEl = document.getElementById('editarAdminAsociacion');
            const conjuntoEl = document.getElementById('editarAdminConjunto');
            if (rolEl) rolEl.value = rol;
            if (asociacionEl) asociacionEl.value = asociacion;
            if (conjuntoEl) conjuntoEl.value = conjunto;
        });
    });

    eliminarButtons.forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');
            const username = button.getAttribute('data-username') || '';
            const form = document.getElementById('formEliminarAdmin');
            if (form) {
                form.action = `/socios/admins/${id}/eliminar/`;
            }
            const usernameEl = document.getElementById('eliminarAdminUsername');
            if (usernameEl) usernameEl.textContent = username;
        });
    });

    const filtrosForm = document.getElementById('adminsFiltrosForm');
    const searchInput = document.getElementById('inputAdminBusqueda');
    const activoSelect = document.getElementById('selectAdminActivo');
    let debounceTimer = null;

    const submitFiltros = function () {
        if (filtrosForm) {
            filtrosForm.submit();
        }
    };

    const scheduleSubmit = function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(submitFiltros, 300);
    };

    if (searchInput) {
        searchInput.addEventListener('input', scheduleSubmit);
    }

    if (activoSelect) {
        activoSelect.addEventListener('change', scheduleSubmit);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAdminModals);
} else {
    setupAdminModals();
}
