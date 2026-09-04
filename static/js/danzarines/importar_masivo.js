document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('formSubirExcel');
    if (!form) return;

    form.addEventListener('submit', function () {
        const input = form.querySelector('input[type="file"]');
        if (!input || !input.files.length) {
            alert('Selecciona un archivo .xlsx antes de continuar.');
            event.preventDefault();
        }
    });
});
