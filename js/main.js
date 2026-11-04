// 메뉴·플로팅 버튼·활용 예 슬라이더·문의 보조 기능.
// 스크립트가 없어도 모든 내용과 링크는 그대로 보이고 쓸 수 있다(점진적 향상).
(() => {
  const toggle = document.querySelector('.menu-toggle');
  const menu = document.querySelector('.site-nav');
  if (!toggle || !menu) return;
  toggle.hidden = false;
  document.documentElement.classList.add('js');
  const small = matchMedia('(max-width: 1023px)');
  const setMenu = (open, restoreFocus = false) => {
    menu.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
    document.body.classList.toggle('menu-open', open && small.matches); // 전체 화면 메뉴일 때만 스크롤 잠금
    if (restoreFocus) toggle.focus();
  };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  menu.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && menu.classList.contains('is-open')) setMenu(false, true); });
  small.addEventListener('change', () => setMenu(false));
})();

// 플로팅 문의 버튼: 첫 화면을 지나면 나타나고, 푸터가 보이면 숨는다
(() => {
  const quick = document.querySelector('.quick');
  const footer = document.querySelector('.site-footer');
  if (!quick || !footer) return;
  let footerVisible = false;
  new IntersectionObserver(([entry]) => { footerVisible = entry.isIntersecting; update(); }).observe(footer);
  function update() { quick.classList.toggle('visible', scrollY > innerHeight * 0.6 && !footerVisible); }
  addEventListener('scroll', update, { passive: true });
  update();
})();

// 활용 예 슬라이더: 스크립트가 없으면 모든 사례가 차례로 보인다
(() => {
  const root = document.querySelector('[data-cases]');
  if (!root) return;
  const slides = [...root.querySelectorAll('.case')];
  const count = root.querySelector('.case-count');
  const dots = [...root.querySelectorAll('.cases-index [data-go]')];
  const controls = root.querySelector('.case-controls');
  if (slides.length < 2 || !controls) return;
  controls.hidden = false;
  let current = 0;
  const show = i => {
    current = (i + slides.length) % slides.length;
    slides.forEach((s, n) => { s.hidden = n !== current; if (n === current) { s.classList.remove('case-swap'); void s.offsetWidth; s.classList.add('case-swap'); } });
    dots.forEach((d, n) => d.toggleAttribute('aria-current', n === current));
    if (count) count.textContent = `${String(current + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
  };
  root.querySelector('[data-prev]').addEventListener('click', () => show(current - 1));
  root.querySelector('[data-next]').addEventListener('click', () => show(current + 1));
  dots.forEach((d, n) => d.addEventListener('click', () => show(n)));
  root.addEventListener('keydown', e => { if (e.key === 'ArrowLeft') show(current - 1); if (e.key === 'ArrowRight') show(current + 1); });
  show(0);
})();

(() => {
  const ADDRESS = 'homepage@avalonx.kr';
  // 제품 페이지에서 ?product=judge 처럼 들어오면 메일 제목에 제품명을 미리 넣는다
  const compose = document.querySelector('#compose-email');
  if (compose) {
    const products = { studio: 'Toaster Studio', forge: 'Toaster Forge', judge: 'Toaster Judge', index: 'Toaster Index', agent: 'Toaster Agent' };
    const product = products[new URLSearchParams(location.search).get('product')];
    const subject = product ? `[AvalonX] ${product} 도입 문의` : '[AvalonX] 도입 문의';
    compose.href = `mailto:${ADDRESS}?subject=${encodeURIComponent(subject)}`;
  }
  // 주소 복사: 클립보드가 안 되면 주소를 선택해 직접 복사하게 한다
  const copyButton = document.querySelector('#copy-email');
  const status = document.querySelector('.copy-status');
  if (!copyButton || !status) return;
  copyButton.hidden = false;
  copyButton.addEventListener('click', async () => {
    try {
      if (!navigator.clipboard?.writeText) throw new Error('clipboard unavailable');
      await navigator.clipboard.writeText(ADDRESS);
      status.textContent = '이메일 주소를 복사했습니다.';
    } catch {
      const address = document.querySelector('.mail-big');
      const selection = getSelection();
      if (address && selection) {
        const range = document.createRange();
        range.selectNodeContents(address);
        selection.removeAllRanges();
        selection.addRange(range);
      }
      status.textContent = '주소를 선택했습니다. 복사 단축키로 복사해 주세요.';
    }
  });
})();
