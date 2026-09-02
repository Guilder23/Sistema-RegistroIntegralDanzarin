document.addEventListener('DOMContentLoaded', function () {
    const asociacion = document.getElementById('crearSocioAsociacion');
    const conjunto = document.getElementById('crearSocioConjunto');
    const bloque = document.getElementById('crearSocioBloque');
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
