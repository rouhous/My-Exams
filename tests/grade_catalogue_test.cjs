const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('exams.html', 'utf8');
const script = fs.readFileSync('shared/grade-catalogue.js', 'utf8');
assert.equal((html.match(/class="om-card"/g) || []).length, 8);
assert.doesNotMatch(html, /id="(?:quick|full-exams|listening)"/);
class Element {
  constructor() { this.children = []; this.value = ''; this.hidden = true; this.classList = {add() {}}; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute() {}
  add(option) { if (!this.children.length) this.value = option.value; this.append(option); }
  addEventListener(name, handler) { this[name] = handler; }
}
function page(search, grade) {
  const nodes = new Map();
  const get = id => {
    if (!nodes.has(id)) nodes.set(id, new Element());
    return nodes.get(id);
  };
  vm.runInNewContext(script, {URLSearchParams, location:{search}, Option: class {
    constructor(text, value) { this.textContent = text; this.value = String(value); }
  }, document:{body:{dataset:{grade}}, getElementById:get, createElement:()=>new Element()}});
  return get;
}
for(const [grade,count] of [[5,4],[6,3],[7,3],[8,3],[9,3],[10,4],[11,4],[12,4]]) {
  const tracks = grade >= 11 ? ['core','elective'] : [''];
  if (grade >= 11) {
    const chooser = page('?grade='+grade);
    assert.equal(chooser('chooseTrack').hidden, false);
    assert.equal(chooser('gradeContent').hidden, true);
    assert.match(chooser('coreLink').href,/track=core$/);
    assert.match(chooser('electiveLink').href,/track=elective$/);
  }
  for(const track of tracks) {
    const get = page('?grade='+grade+(track ? '&track='+track : ''));
    const cards = get('units').children;
    assert.equal(cards.length,count+2);
    assert.equal(cards[count].children[0].textContent,'اختبار شامل');
    assert.equal(cards[count+1].children[0].textContent,'اختبار عشوائي');
    assert.match(cards[count+1].href,/mode=random/);
    for(const link of [...cards,...get('skills').children]) assert(fs.existsSync(link.href.split('?')[0]),link.href);
  }
}
const nine=page('?grade=9&unit=3');
assert.match(nine('units').children[2].href,/unit-exams\/index\.html\?unit=3/);
assert.match(nine('skills').children[0].href,/unit=3&mode=skill&skill=0$/);
const elective=page('?track=12-elective&unit=4','12');
assert.match(elective('skills').children[0].href,/paper-a-preview\.html\?unit=4&mode=skill&skill=lst1$/);
const core=page('?grade=11&track=core&unit=2');
assert.match(core('skills').children[0].href,/paper-b-preview\.html\?mode=skill&skill=lst1$/);
console.log('PASS eight grades, two track choices, unit counts, existing routes and selected-unit skills.');
