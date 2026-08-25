document.addEventListener('DOMContentLoaded', function () {
    // Mobile Navbar Toggle
    const mobileNavToggle = document.getElementById('mobileNavToggle');
    const mobileNav = document.getElementById('mobileNav');
    const mobileNavOverlay = document.getElementById('mobileNavOverlay');
    const mobileNavClose = document.getElementById('mobileNavClose');
    const body = document.body;

    let scrollLockY = 0;

    function lockBodyScroll() {
        scrollLockY = window.scrollY || document.documentElement.scrollTop;
        body.classList.add('navbar-inicio-scroll-locked');
        body.style.top = '-' + scrollLockY + 'px';
    }

    function unlockBodyScroll() {
        if (!body.classList.contains('navbar-inicio-scroll-locked')) {
            body.style.top = '';
            return;
        }
        body.classList.remove('navbar-inicio-scroll-locked');
        body.style.top = '';
        window.scrollTo(0, scrollLockY);
    }

    function openMobileNav() {
        mobileNav.classList.add('active');
        mobileNavOverlay.classList.add('active');
        lockBodyScroll();
    }

    function closeMobileNav() {
        mobileNav.classList.remove('active');
        mobileNavOverlay.classList.remove('active');
        unlockBodyScroll();
    }

    if (mobileNavToggle) {
        mobileNavToggle.addEventListener('click', openMobileNav);
    }

    if (mobileNavClose) {
        mobileNavClose.addEventListener('click', closeMobileNav);
    }

    if (mobileNavOverlay) {
        mobileNavOverlay.addEventListener('click', closeMobileNav);
    }

    // Close nav when clicking links
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-links .nav-link');
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', closeMobileNav);
    });



    // Filter Dropdown Toggle (Bootstrap-like behavior)
    const navFilterBtn = document.getElementById('navFilterBtn');
    const navFilterDropdown = document.getElementById('navFilterDropdown');

    if (navFilterBtn && navFilterDropdown) {
        navFilterBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            navFilterDropdown.classList.toggle('show');
        });

        document.addEventListener('click', function(e) {
            if (!navFilterBtn.contains(e.target) && !navFilterDropdown.contains(e.target)) {
                navFilterDropdown.classList.remove('show');
            }
        });
    }

    window.addEventListener('resize', function () {
        if (window.innerWidth > 991 && mobileNav && mobileNav.classList.contains('active')) {
            closeMobileNav();
        }
        if (window.innerWidth > 991) {
            unlockBodyScroll();
        }
    });
});
