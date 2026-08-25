document.addEventListener('DOMContentLoaded', function () {
    const usernameInput = document.querySelector('#id_username');
    const passwordInput = document.querySelector('#id_password');
    const toggleButton = document.querySelector('#togglePassword');
    const eyeIcon = document.querySelector('#eyeIcon');

    usernameInput?.focus();

    if (toggleButton && passwordInput && eyeIcon) {
        toggleButton.addEventListener('click', function () {
            const isPasswordHidden = passwordInput.type === 'password';

            passwordInput.type = isPasswordHidden ? 'text' : 'password';
            eyeIcon.classList.toggle('fa-eye', !isPasswordHidden);
            eyeIcon.classList.toggle('fa-eye-slash', isPasswordHidden);
            toggleButton.setAttribute('aria-pressed', String(isPasswordHidden));
            toggleButton.setAttribute(
                'aria-label',
                isPasswordHidden ? 'Ocultar contrasena' : 'Mostrar contrasena'
            );
        });
    }
});
