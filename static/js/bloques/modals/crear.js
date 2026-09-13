document.addEventListener('DOMContentLoaded', function () {
    const asociacionSelect = document.getElementById('crearBloqueAsociacion');
    const conjuntoSelect = document.getElementById('crearBloqueConjunto');

    if (!asociacionSelect || !conjuntoSelect) return;

    const filtrarConjuntos = function () {
        Array.from(conjuntoSelect.options).forEach(function (option) {
            const visible = option.dataset.asociacion === asociacionSelect.value;
            option.hidden = !visible;
            option.disabled = !visible;
        });
        if (conjuntoSelect.selectedOptions[0]?.disabled) conjuntoSelect.value = '';
    };

    asociacionSelect.addEventListener('change', filtrarConjuntos);
    filtrarConjuntos();
});
