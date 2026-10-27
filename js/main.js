// Navigation and progressive enhancements. All content remains usable without JavaScript.
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
  const desktop = matchMedia('(min-width: 761px)');
  desktop.addEventListener('change', () => setMenu(false));
})();

(() => {
  const copyButton = document.querySelector('#copy-email');
  const status = document.querySelector('.copy-status');
  if (copyButton && status) {
    copyButton.hidden = false;
    copyButton.addEventListener('click', async () => {
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText('homepage@avalonx.kr');
        status.textContent = '이메일 주소를 복사했습니다.';
      } catch {
        const address = document.querySelector('.email-address');
        const selection = window.getSelection();
        if (address && selection) {
          const range = document.createRange();
          range.selectNodeContents(address);
          selection.removeAllRanges();
          selection.addRange(range);
        }
        status.textContent = '주소를 선택했습니다. 복사 단축키 또는 길게 누르기로 복사해주세요.';
      }
    });
    const products = {'data-studio':'Data Studio',trainer:'Trainer',autojudge:'AutoJudge'};
    const product = products[new URLSearchParams(location.search).get('product')];
    const compose = document.querySelector('#compose-email');
    if (product && compose) compose.href = 'mailto:homepage@avalonx.kr?subject=' + encodeURIComponent('[AvalonX] ' + product + ' 도입 문의');
  }
})();
