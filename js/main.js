// 메뉴와 문의 페이지 보조 기능. 스크립트가 없어도 모든 내용과 링크는 그대로 쓸 수 있다.
(() => {
  const toggle = document.querySelector('.menu-toggle');
  const menu = document.querySelector('.site-nav');
  if (!toggle || !menu) return;
  toggle.hidden = false;
  document.documentElement.classList.add('js');
  const setMenu = (open, restoreFocus = false) => {
    menu.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
    if (restoreFocus) toggle.focus();
  };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  menu.addEventListener('click', event => { if (event.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && menu.classList.contains('is-open')) setMenu(false, true); });
  document.addEventListener('click', event => { if (!event.target.closest('.site-header')) setMenu(false); });
  matchMedia('(min-width: 761px)').addEventListener('change', () => setMenu(false));
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
      const address = document.querySelector('.addr');
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
