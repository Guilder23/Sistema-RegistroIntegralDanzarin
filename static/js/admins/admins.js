// JS para admins

function setupAdminModals() {
    const verButtons = document.querySelectorAll('.btn-ver-admin');
    const editarButtons = document.querySelectorAll('.btn-editar-admin');
    const eliminarButtons = document.querySelectorAll('.btn-eliminar-admin');

    verButtons.forEach(button => {
        button.addEventListener('click', () => {
            const username = button.getAttribute('data-username') || '';
            const fullname = button.getAttribute('data-fullname') || '';
            const email = button.getAttribute('data-email') || '';
            const usernameEl = document.getElementById('verAdminUsername');
            const nombreEl = document.getElementById('verAdminNombre');
            const emailEl = document.getElementById('verAdminEmail');
            if (usernameEl) usernameEl.textContent = username;
            if (nombreEl) nombreEl.textContent = fullname;
            if (emailEl) emailEl.textContent = email;
        });
    });

    editarButtons.forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');
            const username = button.getAttribute('data-username') || '';
            const firstName = button.getAttribute('data-first-name') || '';
            const lastName = button.getAttribute('data-last-name') || '';
            const email = button.getAttribute('data-email') || '';
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
