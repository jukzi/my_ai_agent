import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';

const html = readFileSync(process.env.AGENT_HTML || new URL('../agent.html', import.meta.url), 'utf8');
const source = html.match(/const GitHub = (\{[\s\S]*?\n    \});/)?.[1];
assert.ok(source);
const parent = 'a'.repeat(40);
const next = 'b'.repeat(40);

function fixture(heads) {
  const client = new Function('normalizePath', `return (${source});`)(p => p);
  const writes = [];
  client.resolveRepo = () => 'owner/repo';
  client.request = async (url, method = 'GET', body) => {
    if (method !== 'GET') writes.push({method, body});
    if (url.includes('/ref/heads/')) return {object:{sha:heads.shift()}};
    if (method === 'GET' && url.includes('/commits/')) return {tree:{sha:'base'}};
    if (method === 'GET' && url.includes('/trees/')) return {tree:[{path:'script', mode:'100755'}]};
    if (method === 'POST' && url.endsWith('/trees')) return {sha:'updated-tree'};
    if (method === 'POST' && url.endsWith('/commits')) return {sha:next};
    if (method === 'PATCH' && url.endsWith('/refs/heads/ai/cubature')) return {};
    throw new Error(`Unexpected request: ${method} ${url}`);
  };
  return {writes, run: () => client.commitFiles({branch:'ai/cubature', expected_head:parent, message:'Batch', files:[{path:'script', content:'a'}, {path:'notes', content:'b'}]})};
}

test('publishes both files in one non-forced commit and preserves executable mode', async () => {
  const {run, writes} = fixture([parent,parent]);
  assert.equal((await run()).commit_sha, next);
  assert.deepEqual(writes.map(w => w.method), ['POST','POST','PATCH']);
  assert.deepEqual(writes[0].body.tree.map(e => e.mode), ['100755','100644']);
  assert.deepEqual(writes[1].body.parents, [parent]);
  assert.deepEqual(writes[2].body, {sha:next, force:false});
});

test('rejects an initially stale HEAD before writing', async () => {
  const {run, writes} = fixture([next]);
  await assert.rejects(run(), /Branchstand geändert/);
  assert.deepEqual(writes, []);
});

test('does not update a branch that moved during preparation', async () => {
  const {run, writes} = fixture([parent,next]);
  await assert.rejects(run(), /Branchstand geändert/);
  assert.deepEqual(writes.map(w => w.method), ['POST','POST']);
});
