/* ===========================
   AvalonX Main JavaScript
   =========================== */

const nav = document.querySelector('.nav');
const toggle = document.querySelector('.nav-mobile-toggle');
const navLinks = document.querySelector('.nav-links');

window.addEventListener('scroll', () => {
  nav?.classList.toggle('scrolled', window.scrollY > 20);
});

toggle?.addEventListener('click', () => {
  const isOpen = navLinks?.classList.toggle('open');
  toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
});

const currentPage = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav-links a').forEach((link) => {
  const href = link.getAttribute('href');
  if (href === currentPage || (currentPage === '' && href === 'index.html')) {
    link.classList.add('active');
  }

  link.addEventListener('click', () => {
    navLinks?.classList.remove('open');
    toggle?.setAttribute('aria-expanded', 'false');
  });
});

const revealElements = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
if ('IntersectionObserver' in window && revealElements.length > 0) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  revealElements.forEach((element) => observer.observe(element));
} else {
  revealElements.forEach((element) => element.classList.add('visible'));
}

const submitButtonLabel = document.querySelector('#contact-submit-btn span');
if (submitButtonLabel) {
  submitButtonLabel.textContent = '문의 보내기';
}

const form = document.getElementById('contact-form');
if (form) {
  form.addEventListener('submit', (event) => {
    event.preventDefault();

    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    const submitButton = form.querySelector('button[type="submit"]');
    const originalHTML = submitButton.innerHTML;
    submitButton.innerHTML = '<span>접수되었습니다</span>';
    submitButton.style.background = '#3D7A5F';
    submitButton.disabled = true;

    window.setTimeout(() => {
      submitButton.innerHTML = originalHTML;
      submitButton.style.background = '';
      submitButton.disabled = false;
      form.reset();
    }, 2400);
  });
}

document.querySelectorAll('.cap-card, .card').forEach((card) => {
  card.addEventListener('mousemove', (event) => {
    const rect = card.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width - 0.5) * 8;
    const y = ((event.clientY - rect.top) / rect.height - 0.5) * 8;
    card.style.transform = `perspective(600px) rotateY(${x}deg) rotateX(${-y}deg) translateY(-6px)`;
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
  });
});
