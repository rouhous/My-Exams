/* Present one activity at a time while retaining the original question controls. */
(() => {
  'use strict';
  const script = document.currentScript;
  const host = document.getElementById(script.dataset.host);
  if (!host) return;
  const selector = script.dataset.sections || '[data-activity], section.section, section.part, section.task, section.exam-part';
  const group = script.dataset.group ? document.getElementById(script.dataset.group) : host.parentElement;
  const reading = window.MyExamsSplitPanels;
  const nav = document.createElement('nav');
  nav.className = 'exam-page-nav';
  nav.setAttribute('aria-label', 'Exam pages');
  nav.innerHTML = '<button type="button" data-previous aria-label="Previous page">← <span>Previous</span></button>' +
    '<div><strong data-page-title></strong><small data-page-count aria-live="polite"></small></div>' +
    '<button type="button" data-next aria-label="Next page"><span>Next</span> →</button>';
  nav.hidden = true;
  host.before(nav);
  const previous = nav.querySelector('[data-previous]');
  const next = nav.querySelector('[data-next]');
  const title = nav.querySelector('[data-page-title]');
  const count = nav.querySelector('[data-page-count]');
  let pages = [];
  let index = 0;

  function setPage(i, interact) {
    if (i < 0 || i >= pages.length) return;
    const was = pages[index];
    index = i;
    if (interact && was && was !== pages[i]) {
      was.querySelectorAll('audio').forEach(audio => audio.pause());
    }
    pages.forEach((page, n) => {
      page.dataset.examPage = String(n + 1);
      page.hidden = n !== i;
    });
    const active = pages[i];
    group.classList.toggle('exam-showing-details', active.hasAttribute('data-student-sheet'));
    previous.disabled = i === 0;
    next.disabled = i === pages.length - 1;
    title.textContent = active.getAttribute('data-page-title') ||
      active.querySelector('h2, h3')?.textContent.trim() || '';
    count.textContent = (i + 1) + ' / ' + pages.length;
    host.dispatchEvent(new CustomEvent('exam:page', { detail: { index: i, studentSheet: active.hasAttribute('data-student-sheet'), user: interact } }));
    if (interact) {
      window.scrollTo({ top: Math.max(0, window.scrollY + host.getBoundingClientRect().top - nav.offsetHeight - 12), behavior: 'instant' });
      const heading = active.querySelector('h2, h3');
      if (heading) {
        heading.tabIndex = -1;
        heading.focus({ preventScroll: true });
      }
    }
  }

  function refresh() {
    const updated = [...host.children].filter(child => child.matches(selector + ', [data-student-sheet]'));
    if (updated.length === pages.length && updated.every((page, i) => page === pages[i])) return;
    pages = updated;
    document.body.classList.toggle('exam-single-activity', pages.length === 1 && !!host.querySelector('[data-reading], .exam-dual-grid'));
    nav.hidden = pages.length < 2;
    host.classList.toggle('exam-is-paged', pages.length > 1);
    if (pages.length) {
      setPage(0, false);
      reading?.refresh();
    } else {
      group.classList.remove('exam-showing-details');
    }
  }

  previous.addEventListener('click', () => setPage(index - 1, true));
  next.addEventListener('click', () => setPage(index + 1, true));
  for (const id of (script.dataset.reset || '').split(',').filter(Boolean)) {
    document.getElementById(id)?.addEventListener('click', () => {
      if (pages.length) setPage(0, false);
    });
  }

  window.MyExamsPages = {
    refresh,
    restore(i) {
      if (Number.isInteger(i) && pages.length) setPage(Math.max(0, Math.min(i, pages.length - 1)), false);
    }
  };
  new MutationObserver(refresh).observe(host, { childList: true });
  refresh();
})();
