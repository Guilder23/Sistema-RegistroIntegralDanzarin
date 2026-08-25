document.addEventListener('DOMContentLoaded', function () {
    const formFiltros = document.getElementById('formFiltrosUsuarios');
    const inputBuscar = document.getElementById('buscarUsuario');
    const rolUsuario = document.getElementById('rolUsuario');
    const estadoUsuario = document.getElementById('estadoUsuario');
    const verButtons = document.querySelectorAll('.btn-ver-usuario');
    const editarButtons = document.querySelectorAll('.btn-editar-usuario');
    const formEditar = document.getElementById('formEditarUsuario');

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
            document.getElementById('verUsuarioRol').textContent = this.dataset.isStaff === '1' ? 'Administrador' : 'Usuario';
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
            document.getElementById('editUsuarioIsAdmin').checked = this.dataset.isStaff === '1';
        });
    });
});
