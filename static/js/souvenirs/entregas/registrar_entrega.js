document.addEventListener('DOMContentLoaded', function () {
    const eventoSelect = document.getElementById('selectEvento');
    const souvenirSelect = document.getElementById('selectSouvenir');
    const socioSearch = document.getElementById('socioSearch');
    const socioIdInput = document.getElementById('socioId');
    const socioSuggestions = document.getElementById('socioSuggestions');
    const formRegistrarEntrega = document.getElementById('formRegistrarEntrega');
    const sociosData = document.getElementById('sociosData');
    const asociacionSelect = document.getElementById('selectEntregaAsociacion');
    const conjuntoSelect = document.getElementById('selectEntregaConjunto');

    const socios = sociosData ? JSON.parse(sociosData.textContent) : [];
    const souvenirOptions = souvenirSelect ? Array.from(souvenirSelect.querySelectorAll('option')).map(option => ({
        value: option.value,
        text: option.textContent,
        eventoId: option.dataset.evento || '',
        disabled: option.value === '',
        asociacionId: option.dataset.asociacionId || '',
        conjuntoId: option.dataset.conjuntoId || '',
    })) : [];

    const eventoOptions = eventoSelect ? Array.from(eventoSelect.options).map(option => ({
        element: option,
        value: option.value,
        asociacionId: option.dataset.asociacionId || '',
        conjuntoId: option.dataset.conjuntoId || '',
    })) : [];

    const getScopeReady = function () {
        return Boolean(asociacionSelect?.value && conjuntoSelect?.value);
    };

    const filterEvents = function () {
        const asociacionId = asociacionSelect?.value || '';
        const conjuntoId = conjuntoSelect?.value || '';
        eventoOptions.forEach(optionData => {
            if (!optionData.value) return;
            const valid = optionData.asociacionId === asociacionId
                && (!optionData.conjuntoId || optionData.conjuntoId === conjuntoId);
            optionData.element.hidden = !valid;
            optionData.element.disabled = !valid;
        });
        if (eventoSelect) {
            eventoSelect.disabled = !getScopeReady();
            if (!getScopeReady() || eventoSelect.selectedOptions[0]?.disabled) eventoSelect.value = '';
        }
        renderSouvenirs();
    };

    const renderSouvenirs = function () {
        if (!souvenirSelect) return;
        const selectedEvento = eventoSelect ? eventoSelect.value : '';
        souvenirSelect.innerHTML = '';

        const placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = selectedEvento ? '(Seleccionar si aplica)' : 'Selecciona un evento primero';
        souvenirSelect.appendChild(placeholder);

        if (!selectedEvento) {
            souvenirSelect.disabled = true;
            return;
        }

        const filtered = souvenirOptions.filter(option => option.eventoId === selectedEvento && option.asociacionId === (asociacionSelect?.value || '') && (option.conjuntoId === '' || option.conjuntoId === (conjuntoSelect?.value || '')));
        filtered.forEach(optionData => {
            const option = document.createElement('option');
            option.value = optionData.value;
            option.textContent = optionData.text;
            option.dataset.evento = optionData.eventoId;
            souvenirSelect.appendChild(option);
        });

        souvenirSelect.disabled = false;
    };

    const sociosDisponibles = function () {
        const asociacionId = asociacionSelect?.value || '';
        const conjuntoId = conjuntoSelect?.value || '';
        const eventoId = eventoSelect?.value || '';
        return socios.filter(socio => socio.asociacionId === asociacionId && socio.conjuntoId === conjuntoId && Boolean(eventoId));
    };

    const clearSuggestions = function () {
        socioSuggestions.innerHTML = '';
        socioSuggestions.classList.remove('visible');
    };

    const renderSuggestions = function (query) {
        const searchTerm = query.trim().toLowerCase();
        socioSuggestions.innerHTML = '';

        if (!searchTerm) {
            clearSuggestions();
            socioIdInput.value = '';
            return;
        }

        const matches = sociosDisponibles().filter(socio => socio.label.toLowerCase().includes(searchTerm));
        if (!matches.length) {
            const noMatch = document.createElement('div');
            noMatch.className = 'autocomplete-no-match';
            noMatch.textContent = 'No se encontraron coincidencias';
            socioSuggestions.appendChild(noMatch);
            socioSuggestions.classList.add('visible');
            socioIdInput.value = '';
            return;
        }

        matches.slice(0, 8).forEach(socio => {
            const item = document.createElement('button');
            item.type = 'button';
            item.className = 'autocomplete-item';
            item.textContent = socio.label;
            item.dataset.value = socio.value;
            item.addEventListener('click', function () {
                socioSearch.value = socio.label;
                socioIdInput.value = socio.value;
                clearSuggestions();
            });
            socioSuggestions.appendChild(item);
        });
        socioSuggestions.classList.add('visible');
    };

    if (socioSearch) {
        socioSearch.disabled = true;
        socioSearch.addEventListener('input', function (event) {
            socioIdInput.value = '';
            renderSuggestions(event.target.value);
        });

        socioSearch.addEventListener('focus', function () {
            renderSuggestions(socioSearch.value);
        });

        socioSearch.addEventListener('blur', function () {
            setTimeout(clearSuggestions, 150);
        });
    }

    if (formRegistrarEntrega) {
        formRegistrarEntrega.addEventListener('submit', function (event) {
            if (!socioIdInput.value) {
                event.preventDefault();
                socioSearch.focus();
                alert('Selecciona un socio de la lista antes de guardar.');
            }
            if (!eventoSelect.value || !souvenirSelect.value || !getScopeReady()) {
                event.preventDefault();
                alert('Selecciona asociación, conjunto, evento y souvenir antes de guardar.');
            }
        });
    }

    if (eventoSelect) {
        eventoSelect.addEventListener('change', function () {
            socioSearch.disabled = !eventoSelect.value;
            socioIdInput.value = '';
            socioSearch.value = '';
            renderSouvenirs();
        });
        renderSouvenirs();
    }
    asociacionSelect?.addEventListener('change', function () {
        if (conjuntoSelect && !conjuntoSelect.disabled) conjuntoSelect.value = '';
        socioSearch.disabled = true;
        socioIdInput.value = '';
        socioSearch.value = '';
        filterEvents();
    });
    conjuntoSelect?.addEventListener('change', function () {
        socioSearch.disabled = true;
        socioIdInput.value = '';
        socioSearch.value = '';
        filterEvents();
    });
    filterEvents();
});
