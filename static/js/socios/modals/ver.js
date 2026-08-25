document.addEventListener('DOMContentLoaded', function () {
    const modalVer = document.getElementById('modalVerSocio');
    if (!modalVer) return;

    modalVer.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const setText = (idName, text) => { const el = document.getElementById(idName); if (!el) return; el.textContent = text; };
        setText('verCodigoSocio', button.getAttribute('data-codigo-socio') || '');
        setText('verNombre', button.getAttribute('data-nombre') || '');
        setText('verApellidoPaterno', button.getAttribute('data-apellido-paterno') || '');
        setText('verApellidoMaterno', button.getAttribute('data-apellido-materno') || '');
        setText('verEmail', button.getAttribute('data-email') || '');
        setText('verTelefono', button.getAttribute('data-telefono') || '');
        setText('verCiudad', button.getAttribute('data-ciudad') || '');
        setText('verDireccion', button.getAttribute('data-direccion') || '');
        setText('verCarnetCi', button.getAttribute('data-carnet-ci') || '');
        setText('verCarnetComplemento', button.getAttribute('data-carnet-complemento') || '');
        setText('verFechaNacimiento', button.getAttribute('data-fecha-nacimiento') || '');
        setText('verRazon', button.getAttribute('data-razon') || '');
        setText('verEstado', button.getAttribute('data-estado') || '');
        setText('verSouvenir', button.getAttribute('data-souvenir') || '');
        setText('verFechaIngreso', button.getAttribute('data-fecha-ingreso') || '');
        setText('verObservacion', button.getAttribute('data-observacion') || '');
    });
    // Fallback: poblar también al hacer click en el botón
    document.querySelectorAll('.btn-ver-socio').forEach(btn => {
        btn.addEventListener('click', function (e) {
            const button = e.currentTarget;
            const setText = (idName, text) => { const el = document.getElementById(idName); if (!el) return; el.textContent = text; };
            setText('verCodigoSocio', button.getAttribute('data-codigo-socio') || '');
            setText('verNombre', button.getAttribute('data-nombre') || '');
            setText('verApellidoPaterno', button.getAttribute('data-apellido-paterno') || '');
            setText('verApellidoMaterno', button.getAttribute('data-apellido-materno') || '');
            setText('verEmail', button.getAttribute('data-email') || '');
            setText('verTelefono', button.getAttribute('data-telefono') || '');
            setText('verCiudad', button.getAttribute('data-ciudad') || '');
            setText('verDireccion', button.getAttribute('data-direccion') || '');
            setText('verCarnetCi', button.getAttribute('data-carnet-ci') || '');
            setText('verCarnetComplemento', button.getAttribute('data-carnet-complemento') || '');
            setText('verFechaNacimiento', button.getAttribute('data-fecha-nacimiento') || '');
            setText('verRazon', button.getAttribute('data-razon') || '');
            setText('verEstado', button.getAttribute('data-estado') || '');
            setText('verSouvenir', button.getAttribute('data-souvenir') || '');
            setText('verFechaIngreso', button.getAttribute('data-fecha-ingreso') || '');
            setText('verObservacion', button.getAttribute('data-observacion') || '');
        });
    });
});
