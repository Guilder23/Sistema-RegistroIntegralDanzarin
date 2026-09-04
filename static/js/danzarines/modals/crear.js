document.addEventListener('DOMContentLoaded', function () {
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
