document.addEventListener('DOMContentLoaded', function () {
    const yearElements = document.querySelectorAll('[data-year]');
    const currentYear = new Date().getFullYear();
    yearElements.forEach(function (el) {
        el.textContent = currentYear;
    });
});
