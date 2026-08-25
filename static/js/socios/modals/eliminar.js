document.addEventListener('DOMContentLoaded', function () {
    const modalEliminar = document.getElementById('modalEliminarSocio');
    if (!modalEliminar) return;

    modalEliminar.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const id = button.getAttribute('data-id');
        document.getElementById('eliminarNombre').textContent = button.getAttribute('data-nombre');
        document.getElementById('formEliminarSocio').action = `/socios/${id}/eliminar/`;
    });
});
