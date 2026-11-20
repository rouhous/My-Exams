/* Synchronize finished practice attempts for a student launched from My English Journey. */
(() => {
  'use strict';
  const endpoint = 'https://xboracsbzikojobumcke.supabase.co/functions/v1/mej-exam-results';
  const key = 'MY_EXAMS_JOURNEY_V1';
  const read = (storage, name) => {
    try { return JSON.parse(storage.getItem(name)); } catch { return null; }
  };
  const session = read(sessionStorage, key);
  if (!session || !/^[a-f0-9]{64}\.\d{13}\.[a-f0-9]{64}$/.test(session.token)) return;
  const studentKey = session.token.split('.')[0];
  const queueKey = 'MY_EXAMS_PENDING_V1:' + studentKey;
  const queued = () => read(localStorage, queueKey) || [];
  const setQueue = rows => {
    if (rows.length) localStorage.setItem(queueKey, JSON.stringify(rows));
    else localStorage.removeItem(queueKey);
  };
  const retry = document.createElement('button');
  retry.type = 'button';
  retry.textContent = 'إعادة إرسال النتيجة';
  retry.hidden = true;
  const banner = document.createElement('p');
  banner.dir = 'rtl';
  banner.setAttribute('role', 'status');
  const label = document.createElement('span');
  banner.append(label, ' ', retry);
  banner.style.cssText = 'margin:.5rem auto;padding:.55rem .8rem;max-width:65rem;background:#e5f1e9;color:#163d2c;border-radius:.5rem';
  document.querySelector('main')?.prepend(banner);
  function status(message, canRetry = false) {
    label.textContent = message;
    retry.hidden = !canRetry;
  }
  function sameSession() {
    return read(sessionStorage, key)?.token === session.token;
  }
  let sending;
  async function flush() {
    if (sending || !sameSession() || !queued().length) return sending;
    if (!navigator.onLine) return status('حُفظت النتيجة على الجهاز وستُرسل عند عودة الاتصال.', true);
    if (Date.now() >= session.expiresAt) return status('حُفظت النتيجة. افتح My Exams مجددًا من رحلتك لإرسالها.');
    sending = (async () => {
      status('جارٍ إرسال النتيجة إلى المعلم…');
      for (const attempt of queued()) {
        if (!sameSession()) return;
        try {
          const response = await fetch(endpoint, {
            method:'POST', credentials:'omit', cache:'no-store', keepalive:true,
            headers:{Authorization:'Bearer ' + session.token, 'Content-Type':'application/json'},
            body:JSON.stringify({action:'submit', ...attempt}), signal:AbortSignal.timeout(12000)
          });
          const data = await response.json();
          if (response.status === 401) return status('حُفظت النتيجة. افتح My Exams مجددًا من رحلتك لإرسالها.');
          if (!response.ok || !data.ok) throw Error(data.error);
          setQueue(queued().filter(row => row.attemptId !== attempt.attemptId));
        } catch {
          return status('النتيجة محفوظة على الجهاز. لم يتأكد إرسالها بعد.', true);
        }
      }
      status('أُرسلت النتيجة إلى بوابة المعلم.');
    })();
    try { return await sending; } finally { sending = null; }
  }
  retry.addEventListener('click', flush);
  window.addEventListener('online', flush);
  window.addEventListener('pageshow', flush);
  const params = new URLSearchParams(location.search);
  const path = location.pathname;
  const gradePath = /\/grade(9|10|11|12)\//.exec(path);
  const fileGrade = Number(params.get('grade') || gradePath?.[1] || session.grade);
  const mixed = path.includes('/mixed-exams/');
  const fileTrack = fileGrade >= 11 ? (params.get('track') || /\/(core|elective)\//.exec(path)?.[1] || '') : '';
  status('My Exams مرتبط بحساب رحلتك. تُرسل النتيجة إلى معلمك بعد التسليم.');
  function report({grade = fileGrade, track = fileTrack, model = '', skill = '', earned, possible, writingPending = false, attemptId}) {
    if (grade !== session.grade || !sameSession()) return;
    const mode = mixed ? (params.get('mode') === 'random' ? 'random' : 'comprehensive') : skill ? 'skill' : 'unit';
    const clean = value => String(value).replace(/[^a-z0-9_/-]/gi,'-');
    const paper = mixed ? mode : clean(model || 'practice').slice(0,90);
    const row = {attemptId:attemptId || crypto.randomUUID(), grade, track, mode, paper, skill:clean(skill).slice(0,32), earned, possible, writingPending};
    if (!Number.isFinite(earned) || !Number.isFinite(possible) || possible < earned || (!possible && !writingPending)) return;
    try {
      const existing = queued();
      if (!existing.some(x => x.attemptId === row.attemptId)) setQueue([...existing, row]);
    } catch {
      status('تعذر حفظ النتيجة على الجهاز لإرسالها.');
      return;
    }
    void flush();
  }
  window.MyExamsJourney = {report, storageKey: name => name + ':' + studentKey};
  void flush();
})();
