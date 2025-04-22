// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar-glass');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Initialize dropdown hover effects
const dropdowns = document.querySelectorAll('.dropdown');
dropdowns.forEach(dropdown => {
    dropdown.addEventListener('mouseenter', function() {
        if (window.innerWidth > 992) { // Desktop only
            const menu = this.querySelector('.dropdown-menu');
            if (menu) {
                menu.style.display = 'block';
            }
        }
    });
    
    dropdown.addEventListener('mouseleave', function() {
        if (window.innerWidth > 992) { // Desktop only
            const menu = this.querySelector('.dropdown-menu');
            if (menu && !menu.classList.contains('show')) {
                menu.style.display = 'none';
            }
        }
    });
});

// Mobile menu close when clicking outside
document.addEventListener('click', function(e) {
    const navbar = document.querySelector('.navbar-collapse');
    const toggler = document.querySelector('.navbar-toggler');
    if (navbar.classList.contains('show') && !e.target.closest('.navbar') && !e.target.closest('.navbar-toggler')) {
        toggler.click();
    }
});