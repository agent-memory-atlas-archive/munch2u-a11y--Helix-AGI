// Execute the actual dashboard functions with a small DOM/fetch harness.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { spawnSync } = require('node:child_process');

const html = fs.readFileSync(path.join(__dirname, '../dashboard/dashboard_ui.html'), 'utf8');
function source(start, end) {
  const a = html.indexOf(start);
  const b = html.indexOf(end, a);
  assert.ok(a >= 0 && b > a, 'Dashboard function boundaries exist');
  return html.slice(a, b);
}
const loadModule = source('async function loadModuleCode', '// Add Module Modal Handlers');
const removeStaged = source('window.deleteStagedFile =', '// Dropzone interactions');
const listStaged = source('async function fetchStagedFiles', 'window.deleteStagedFile =');
const uploadStaged = source('async function uploadStagedFile', '// Initial background poll');
const quiet = { error() {} };

test('dashboard module script parses completely', () => {
  const script = html.match(/<script type="module">([\s\S]*?)<\/script>/);
  assert.ok(script);
  const parsed = spawnSync(process.execPath, ['--input-type=module', '--check'], {
    input: script[1], encoding: 'utf8',
  });
  assert.equal(parsed.status, 0, parsed.stderr);
});

test('module viewer requests encoded source and displays the response', async () => {
  const elements = Object.fromEntries(['module-active-title', 'module-code-view', 'module-active-meta'].map(id => [id, {}]));
  let requested;
  const ctx = vm.createContext({
    activeModule: null, console: quiet,
    document: { querySelectorAll: () => [], getElementById: id => elements[id] },
    fetch: async url => { requested = url; return { ok: true, json: async () => ({ name: 'a b.py', code: 'pass', size: 4 }) }; },
  });
  vm.runInContext(loadModule, ctx);
  await ctx.loadModuleCode('a b.py');
  assert.equal(requested, '/api/modules/a%20b.py');
  assert.equal(elements['module-code-view'].textContent, 'pass');
  assert.equal(elements['module-active-meta'].textContent, '4 bytes');
  ctx.fetch = async () => ({ ok: false, status: 404, json: async () => ({}) });
  await ctx.loadModuleCode('missing.py');
  assert.equal(elements['module-code-view'].textContent, 'pass');
});

test('staged deletion uses its route and refreshes only on success', async () => {
  let requested, options, refreshed = 0;
  const ctx = vm.createContext({
    window: {}, console: quiet,
    fetchStagedFiles: async () => { refreshed++; },
    fetch: async (url, opts) => { requested = url; options = opts; return { ok: true }; },
  });
  vm.runInContext(removeStaged, ctx);
  await ctx.window.deleteStagedFile('a%20b.txt');
  assert.equal(requested, '/api/staged_files/a%20b.txt');
  assert.equal(options.method, 'DELETE');
  assert.equal(refreshed, 1);
  ctx.fetch = async () => ({ ok: false, status: 500 });
  await ctx.window.deleteStagedFile('a%20b.txt');
  assert.equal(refreshed, 1);
});

test('apostrophes in staged filenames use a bound button action', async () => {
  const name = "reader's notes.txt";
  let removed;
  const list = { children: [], appendChild(child) { this.children.push(child); } };
  const ctx = vm.createContext({
    console: quiet, stagedBadgeEl: {}, stagedListEl: list,
    escapeHtml: value => value.replaceAll("'", '&#39;'),
    document: { createElement: () => ({ children: [], appendChild(child) { this.children.push(child); } }) },
    window: { deleteStagedFile: value => { removed = value; } },
    fetch: async () => ({ ok: true, json: async () => ({ staged: [{ name, size: 3 }] }) }),
  });
  vm.runInContext(listStaged, ctx);
  await ctx.fetchStagedFiles();
  const row = list.children[0];
  assert.equal(row.innerHTML.includes('onclick='), false);
  row.children[0].onclick();
  assert.equal(removed, encodeURIComponent(name));
});

test('upload sends multipart file data and reports server failures', async () => {
  let requested, options, errors = 0;
  class FormData { append(key, value) { this[key] = value; } }
  const ctx = vm.createContext({
    FormData, console: { error() { errors++; } },
    fetch: async (url, opts) => { requested = url; options = opts; return { ok: true }; },
  });
  vm.runInContext(uploadStaged, ctx);
  const file = { name: 'notes.txt' };
  await ctx.uploadStagedFile(file);
  assert.equal(requested, '/api/stage_file');
  assert.equal(options.method, 'POST');
  assert.equal(options.body.file, file);
  assert.equal(errors, 0);
  ctx.fetch = async () => ({ ok: false, status: 500 });
  await ctx.uploadStagedFile(file);
  assert.equal(errors, 1);
});
