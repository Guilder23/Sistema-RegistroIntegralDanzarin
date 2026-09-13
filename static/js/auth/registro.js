document.addEventListener('DOMContentLoaded', function () {
    const formFiltros = document.getElementById('formFiltrosUsuarios');
    const inputBuscar = document.getElementById('buscarUsuario');
    const rolUsuario = document.getElementById('rolUsuario');
    const estadoUsuario = document.getElementById('estadoUsuario');
    const verButtons = document.querySelectorAll('.btn-ver-usuario');
    const editarButtons = document.querySelectorAll('.btn-editar-usuario');
    const formEditar = document.getElementById('formEditarUsuario');
    const passwordEditar = document.getElementById('editUsuarioPassword');
    const passwordConfirmarEditar = document.getElementById('editUsuarioPassword2');
    const formEliminar = document.getElementById('formEliminarUsuario');
    const modalEliminar = document.getElementById('modalEliminarUsuario');

    let filtroTimer;
    function enviarFiltros() {
        if (formFiltros) {
            formFiltros.submit();
        }
    }

    inputBuscar?.addEventListener('input', function () {
        clearTimeout(filtroTimer);
        filtroTimer = setTimeout(enviarFiltros, 350);
    });
    rolUsuario?.addEventListener('change', enviarFiltros);
    estadoUsuario?.addEventListener('change', enviarFiltros);

    verButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const firstName = this.dataset.firstName || '';
            const lastName = this.dataset.lastName || '';
            const fullName = `${firstName} ${lastName}`.trim();

            document.getElementById('verUsuarioUsername').textContent = this.dataset.username || '';
            document.getElementById('verUsuarioNombre').textContent = fullName || '-';
            document.getElementById('verUsuarioEmail').textContent = this.dataset.email || '-';
            document.getElementById('verUsuarioRol').textContent = this.dataset.rol || 'Miembro / Danzarín';
            document.getElementById('verUsuarioEstado').textContent = this.dataset.isActive === '1' ? 'Activo' : 'Bloqueado';
        });
    });

    editarButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const userId = this.dataset.id;
            formEditar.action = `/usuarios/${userId}/editar/`;

            document.getElementById('editUsuarioUsername').value = this.dataset.username || '';
            document.getElementById('editUsuarioFirstName').value = this.dataset.firstName || '';
            document.getElementById('editUsuarioLastName').value = this.dataset.lastName || '';
            document.getElementById('editUsuarioEmail').value = this.dataset.email || '';
            document.getElementById('editUsuarioRol').value = this.dataset.rol || 'miembro';
            document.getElementById('editUsuarioAsociacion').value = this.dataset.asociacion || '';
            document.getElementById('editUsuarioConjunto').value = this.dataset.conjunto || '';
        });
    });

    const validarConfirmacionPassword = function () {
        if (!passwordEditar || !passwordConfirmarEditar) return true;
        const quiereCambiarPassword = Boolean(passwordEditar.value);
        passwordConfirmarEditar.required = quiereCambiarPassword;
        if (!quiereCambiarPassword) {
            passwordConfirmarEditar.setCustomValidity('');
            return true;
        }
        const coincide = passwordEditar.value === passwordConfirmarEditar.value;
        passwordConfirmarEditar.setCustomValidity(coincide ? '' : 'Las contraseñas no coinciden.');
        return coincide;
    };

    passwordEditar?.addEventListener('input', validarConfirmacionPassword);
    passwordConfirmarEditar?.addEventListener('input', validarConfirmacionPassword);
    formEditar?.addEventListener('submit', function (event) {
        if (!validarConfirmacionPassword()) {
            event.preventDefault();
            passwordConfirmarEditar.focus();
        }
    });

    const abrirModalEliminar = function () {
        if (!modalEliminar) return;
        modalEliminar.classList.add('show');
        modalEliminar.style.display = 'block';
        modalEliminar.removeAttribute('aria-hidden');
        modalEliminar.setAttribute('aria-modal', 'true');
        document.body.classList.add('modal-open');
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show modal-backdrop-usuario';
        backdrop.addEventListener('click', cerrarModalEliminar);
        document.body.appendChild(backdrop);
    };

    const cerrarModalEliminar = function () {
        if (!modalEliminar) return;
        modalEliminar.classList.remove('show');
        modalEliminar.style.display = 'none';
        modalEliminar.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-open');
        document.querySelectorAll('.modal-backdrop-usuario').forEach(function (backdrop) {
            backdrop.remove();
        });
    };

    document.querySelectorAll('.btn-eliminar-usuario').forEach(function (btn) {
        btn.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopImmediatePropagation();
            if (formEliminar) formEliminar.action = btn.dataset.action;
            const username = document.getElementById('eliminarUsuarioUsername');
            if (username) username.textContent = btn.dataset.username || '';
            abrirModalEliminar();
        });
    });

    modalEliminar?.querySelectorAll('[data-dismiss="modal"]').forEach(function (button) {
        button.addEventListener('click', cerrarModalEliminar);
    });

    modalEliminar?.addEventListener('click', function (event) {
        if (event.target === modalEliminar) cerrarModalEliminar();
    });
});
