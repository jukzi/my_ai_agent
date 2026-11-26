import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';

const html = readFileSync(new URL('../agent.html', import.meta.url), 'utf8');
const source = html.match(/const GitHub = (\{[\s\S]*?\n    \});/)?.[1];
assert.ok(source, 'GitHub client not found');

function fixture(responses) {
  const calls = [];
  const fetch = async (url, options) => {
    calls.push({url, ...options});
    assert.ok(responses.length, 'Unexpected request');
    const [status, data] = responses.shift();
    return new Response(JSON.stringify(data), {status});
  };
  const client = new Function('fetch', 'state', 'normalizePath', `return (${source});`)(fetch, {config:{githubToken:'test-token'}}, path => path);
  return {calls, commit: () => client.commitFile('owner/repo', 'ai/cubature', 'index.html', 'new content', 'Update')};
}

const file = sha => [200, {type:'file', sha}];
const success = [200, {commit:{sha:'new-commit'}}];
const conflict = [409, {message:'original conflict'}];

test('reads the current file SHA without cache and uses it in the write', async () => {
  const {calls, commit} = fixture([file('old'), success]);
  assert.equal((await commit()).commit_sha, 'new-commit');
  assert.equal(calls[0].cache, 'no-store');
  assert.equal(new URL(calls[0].url).searchParams.get('ref'), 'ai/cubature');
  assert.equal(JSON.parse(calls[1].body).sha, 'old');
});

test('404 allows creation, but 403 aborts without writing', async () => {
  const missing = fixture([[404, {message:'not found'}], success]);
  await missing.commit();
  assert.ok(!Object.hasOwn(JSON.parse(missing.calls[1].body), 'sha'));
  const denied = fixture([[403, {message:'denied'}]]);
  await assert.rejects(denied.commit, {status:403});
  assert.equal(denied.calls.length, 1);
});

test('409 rereads without cache and never retries the write', async () => {
  for (const sha of ['old', 'changed']) {
    const {calls, commit} = fixture([file('old'), conflict, file(sha)]);
    await assert.rejects(commit, {status:409, message:sha === 'old' ? /original conflict/ : /seit dem Lesen geändert/});
    assert.deepEqual(calls.map(call => call.method), ['GET', 'PUT', 'GET']);
    assert.equal(calls[2].cache, 'no-store');
  }
});
