document.addEventListener('DOMContentLoaded', function () {
    const formulario = document.querySelector('#modalCrearDanzarin form');
    const apellidoPaterno = formulario?.querySelector('[name="apellido_paterno"]');
    const carnetCi = formulario?.querySelector('[name="carnet_ci"]');
    const username = formulario?.querySelector('[name="username"]');
    const password = formulario?.querySelector('[name="password"]');
    const actualizarCredenciales = function () {
        if (username) username.value = apellidoPaterno?.value.trim() || '';
        if (password) password.value = carnetCi?.value.trim() || '';
    };
    apellidoPaterno?.addEventListener('input', actualizarCredenciales);
    carnetCi?.addEventListener('input', actualizarCredenciales);

    const asociacion = document.getElementById('crearDanzarinAsociacion');
    const conjunto = document.getElementById('crearDanzarinConjunto');
    const bloque = document.getElementById('crearDanzarinBloque');
    const filtrar = function (select, attribute, value) {
        if (!select) return;
        Array.from(select.options).forEach(option => {
            const visible = !option.value || option.dataset[attribute] === value;
            option.hidden = !visible;
            option.disabled = !visible;
        });
        if (select.selectedOptions[0]?.disabled) select.value = '';
    };
    const actualizarConjuntos = function () {
        filtrar(conjunto, 'asociacionId', asociacion?.value || '');
        actualizarBloques();
    };
    const actualizarBloques = function () {
        filtrar(bloque, 'conjuntoId', conjunto?.value || '');
    };
    asociacion?.addEventListener('change', actualizarConjuntos);
    conjunto?.addEventListener('change', actualizarBloques);
    actualizarConjuntos();
});
