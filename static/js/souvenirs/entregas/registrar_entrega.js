document.addEventListener('DOMContentLoaded', function () {
    const eventoSelect = document.getElementById('selectEvento');
    const souvenirSelect = document.getElementById('selectSouvenir');
    const danzarinSearch = document.getElementById('danzarinSearch');
    const danzarinIdInput = document.getElementById('danzarinId');
    const danzarinSuggestions = document.getElementById('danzarinSuggestions');
    const formRegistrarEntrega = document.getElementById('formRegistrarEntrega');
    const danzarinesData = document.getElementById('danzarinesData');
    const asociacionSelect = document.getElementById('selectEntregaAsociacion');
    const conjuntoSelect = document.getElementById('selectEntregaConjunto');

    const danzarines = danzarinesData ? JSON.parse(danzarinesData.textContent) : [];
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

    const danzarinesDisponibles = function () {
        const asociacionId = asociacionSelect?.value || '';
        const conjuntoId = conjuntoSelect?.value || '';
        const eventoId = eventoSelect?.value || '';
        return danzarines.filter(danzarin => danzarin.asociacionId === asociacionId && danzarin.conjuntoId === conjuntoId && Boolean(eventoId));
    };

    const clearSuggestions = function () {
        danzarinSuggestions.innerHTML = '';
        danzarinSuggestions.classList.remove('visible');
    };

    const renderSuggestions = function (query) {
        const searchTerm = query.trim().toLowerCase();
        danzarinSuggestions.innerHTML = '';

        if (!searchTerm) {
            clearSuggestions();
            danzarinIdInput.value = '';
            return;
        }

        const matches = danzarinesDisponibles().filter(danzarin => danzarin.label.toLowerCase().includes(searchTerm));
        if (!matches.length) {
            const noMatch = document.createElement('div');
            noMatch.className = 'autocomplete-no-match';
            noMatch.textContent = 'No se encontraron coincidencias';
            danzarinSuggestions.appendChild(noMatch);
            danzarinSuggestions.classList.add('visible');
            danzarinIdInput.value = '';
            return;
        }

        matches.slice(0, 8).forEach(danzarin => {
            const item = document.createElement('button');
            item.type = 'button';
            item.className = 'autocomplete-item';
            item.textContent = danzarin.label;
            item.dataset.value = danzarin.value;
            item.addEventListener('click', function () {
                danzarinSearch.value = danzarin.label;
                danzarinIdInput.value = danzarin.value;
                clearSuggestions();
            });
            danzarinSuggestions.appendChild(item);
        });
        danzarinSuggestions.classList.add('visible');
    };

    if (danzarinSearch) {
        danzarinSearch.disabled = true;
        danzarinSearch.addEventListener('input', function (event) {
            danzarinIdInput.value = '';
            renderSuggestions(event.target.value);
        });

        danzarinSearch.addEventListener('focus', function () {
            renderSuggestions(danzarinSearch.value);
        });

        danzarinSearch.addEventListener('blur', function () {
            setTimeout(clearSuggestions, 150);
        });
    }

    if (formRegistrarEntrega) {
        formRegistrarEntrega.addEventListener('submit', function (event) {
            if (!danzarinIdInput.value) {
                event.preventDefault();
                danzarinSearch.focus();
                alert('Selecciona un danzarín de la lista antes de guardar.');
            }
            if (!eventoSelect.value || !souvenirSelect.value || !getScopeReady()) {
                event.preventDefault();
                alert('Selecciona asociación, conjunto, evento y souvenir antes de guardar.');
            }
        });
    }

    if (eventoSelect) {
        eventoSelect.addEventListener('change', function () {
            danzarinSearch.disabled = !eventoSelect.value;
            danzarinIdInput.value = '';
            danzarinSearch.value = '';
            renderSouvenirs();
        });
        renderSouvenirs();
    }
    asociacionSelect?.addEventListener('change', function () {
        if (conjuntoSelect && !conjuntoSelect.disabled) conjuntoSelect.value = '';
        danzarinSearch.disabled = true;
        danzarinIdInput.value = '';
        danzarinSearch.value = '';
        filterEvents();
    });
    conjuntoSelect?.addEventListener('change', function () {
        danzarinSearch.disabled = true;
        danzarinIdInput.value = '';
        danzarinSearch.value = '';
        filterEvents();
    });
    filterEvents();
});
