(() => {
  'use strict';
  const names = ['الخامس', 'السادس', 'السابع', 'الثامن', 'التاسع', 'العاشر', 'الحادي عشر', 'الثاني عشر'];
  const ordinals = ['الأولى', 'الثانية', 'الثالثة', 'الرابعة'];
  const units = {
    5: ['Talent show', 'Then and now', 'Let’s explore!', 'Off to the shops'],
    6: ['Free-time fun', 'Technology', 'Places'],
    7: ['Entertainment', 'Awesome animals', 'Travel'],
    8: ['Our planet', 'Adventure sports', 'Spend or save?'],
    9: ['Identity', 'Connections', 'The future is now'],
    10: ['New Media', 'Climate Change', 'Renewable Energy', 'Civilisation'],
    '11-core': ['Communication', 'Those Teenage Things', 'Travellers and Tourists', 'Innovation'],
    '11-elective': ['Fame', 'The Mind', 'In the Past', 'Careers'],
    '12-core': ['Retail Therapy', 'Starting University', 'Tourism and Hospitality', 'Travel and Transport'],
    '12-elective': ['The Arts', 'Doing the Right Thing', 'Living in a Changing World', 'Higher Education']
  };
  const standard = [
    ['listening1', 'Listening 1'], ['listening2', 'Listening 2'],
    ['grammar', 'Grammar'], ['vocabulary', 'Vocabulary'], ['reading1', 'Reading 1'],
    ['reading2', 'Reading 2'], ['writing1', 'Writing 1'], ['writing2', 'Writing 2']
  ];
  const upperElective = [
    ['lst1', 'Listening 1'], ['lst2', 'Listening 2'], ['rdg1', 'Reading 1'],
    ['rdg2', 'Reading 2'], ['wrt1', 'Writing 1'], ['wrt2', 'Writing 2']
  ];
  const upperCore = [
    ...upperElective.slice(0, 2), ['grm', 'Grammar'], ['vcb', 'Vocabulary'],
    ...upperElective.slice(2, 4), ['rdg3', 'Reading 3'], ...upperElective.slice(4)
  ];
  const gradeSkills = {
    5: standard, 6: standard,
    7: [['listening1', 'Listening 1'], ['listening2', 'Listening 2'],
      ['grammarvocabulary', 'Grammar & Vocabulary'], ['reading1', 'Reading 1'],
      ['reading2', 'Reading 2'], ['writing1', 'Writing 1'], ['writing2', 'Writing 2']],
    10: [['listening', 'Listening'], ...standard.slice(2), ['dataAnalysis', 'Data Analysis · Charts']]
  };
  gradeSkills[8] = gradeSkills[7];
  gradeSkills[9] = gradeSkills[7];

  const $ = id => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  const requestedGrade = Number(document.body.dataset.grade || params.get('grade'));
  const grade = Number.isInteger(requestedGrade) && requestedGrade >= 5 && requestedGrade <= 12 ? requestedGrade : 5;
  const track = (params.get('track') || '').replace(/^(11|12)-/, '');
  const gradeUrl = grade === 12 ? './grade12-skills.html' : './grade-skills.html?grade=' + grade;
  const divider = grade === 12 ? '?' : '&';
  const isUpper = grade >= 11;
  const gradeName = 'الصف ' + names[grade - 5];

  $('gradeTitle').textContent = 'اختبارات ' + gradeName;
  document.title = $('gradeTitle').textContent + ' | My Exams';
  $('enTitle').textContent = 'Grade ' + grade + ' English Exams';
  if (isUpper && !['core', 'elective'].includes(track)) {
    for (const name of ['core', 'elective']) {
      $(name + 'Link').href = gradeUrl + divider + 'track=' + name;
    }
    $('chooseTrack').hidden = false;
    return;
  }
  if (isUpper) {
    $('trackBack').href = gradeUrl;
    $('trackBack').hidden = false;
    $('enTitle').textContent += track === 'core' ? ' · Core' : ' · Elective';
  }

  const topics = units[isUpper ? grade + '-' + track : grade];
  function unitLink(index, skill) {
    const model = 'ABCD'[index];
    if (grade <= 6) return './grades5-6/index.html?grade=' + grade + '&model=' + model + (skill ? '&skill=' + skill : '&mode=exam');
    if (grade <= 8) return './grades7-8/index.html?grade=' + grade + '&model=' + model + (skill ? '&mode=practice&skill=' + skill : '&mode=exam');
    if (grade === 9) {
      const task = gradeSkills[9].findIndex(([key]) => key === skill);
      return './grade9/unit-exams/index.html?unit=' + (index + 1) + (task < 0 ? '' : '&mode=skill&skill=' + task);
    }
    if (grade === 10) return './grade10/index.html?model=' + model + (skill ? '&mode=practice&skill=' + skill : '&mode=exam');
    const paper = grade === 12 && track === 'elective' ? 'a' : model.toLowerCase();
    const unitQuery = grade === 12 && track === 'elective' ? 'unit=' + (index + 1) + '&' : '';
    return './grade' + grade + '/' + track + '/units/paper-' + paper + '-preview.html?' + unitQuery + (skill ? 'mode=skill&skill=' + skill : 'mode=full');
  }
  function mixedLink(random) {
    const mode = random ? 'random' : 'exam';
    if (grade <= 6) return './grades5-6/index.html?grade=' + grade + '&model=' + (grade === 6 ? 'D' : 'E') + '&mode=' + mode;
    if (grade <= 8) return './grades7-8/index.html?grade=' + grade + '&model=D&mode=' + mode;
    if (grade <= 10) return './grade' + grade + '/index.html?model=' + (grade === 9 ? 'D' : 'E') + '&mode=' + mode;
    if (grade === 11 && track === 'core') return './grade11/core/index.html?model=E&mode=' + mode;
    return './upper-grades-practice.html?track=' + grade + '-' + track + '&model=E&mode=' + (random ? 'random' : 'full');
  }
  function card(url, name, detail, accessibleName) {
    const a = document.createElement('a');
    a.className = 'om-card';
    a.href = url;
    const title = document.createElement('strong');
    title.textContent = name;
    const sub = document.createElement('small');
    sub.textContent = detail;
    a.append(title, sub);
    if (accessibleName) a.setAttribute('aria-label', accessibleName);
    return a;
  }

  topics.forEach((topic, index) => {
    const title = 'الوحدة ' + ordinals[index];
    $('units').append(card(unitLink(index), title, topic));
    $('unit').add(new Option(title + ' · ' + topic, index));
  });
  const mixed = card(mixedLink(false), 'اختبار شامل', 'مراجعة من عدة وحدات');
  const random = card(mixedLink(true), 'اختبار عشوائي', 'أسئلة تتغير عند بدء اختبار جديد');
  mixed.classList.add('om-card-comprehensive');
  random.classList.add('om-card-comprehensive');
  $('units').append(mixed, random);

  const requestedUnit = Number(params.get('unit')) || 'ABCD'.indexOf(params.get('model') || '-') + 1;
  if (requestedUnit >= 1 && requestedUnit <= topics.length) $('unit').value = requestedUnit - 1;
  const skills = isUpper ? (track === 'core' ? upperCore : upperElective) : gradeSkills[grade];
  function showSkills() {
    const unit = Number($('unit').value);
    $('skills').replaceChildren(...skills
      .filter(([key]) => params.get('section') !== 'listening' || /^(lst|listening)/.test(key))
      .map(([key, title]) => card(unitLink(unit, key), title, 'ابدأ التدريب', 'بدء ' + title)));
  }
  $('unit').addEventListener('change', showSkills);
  showSkills();
  $('gradeContent').hidden = false;
})();
