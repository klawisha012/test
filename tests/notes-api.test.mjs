import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createNotesApi, createMockNotesApi } from '../web/notes-api.js';

test('HTTP adapter creates and lists notes according to the contract', async () => {
  const calls = [];
  const note = { id: 12, text: 'Мысль' };
  const api = createNotesApi(async (path, options) => {
    calls.push({ path, ...options });
    return Response.json(options.method === 'POST' ? note : [note]);
  });
  assert.deepEqual(await api.add('Мысль'), note);
  assert.deepEqual(await api.list(), [note]);
  assert.deepEqual(calls, [
    { path: '/notes', method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{"text":"Мысль"}' },
    { path: '/notes', method: 'GET' },
  ]);
});

test('deletion accepts both 204 and an already removed note (404)', async () => {
  for (const status of [204, 404]) {
    const api = createNotesApi(async (path, options) => {
      assert.equal(path, '/notes/12');
      assert.equal(options.method, 'DELETE');
      return new Response(null, { status });
    });
    await api.remove(12);
  }
});

test('other HTTP errors are reported rather than treated as success', async () => {
  const api = createNotesApi(async () => new Response(null, { status: 500 }));
  await assert.rejects(api.list(), /Не удалось/);
  await assert.rejects(api.add('text'), /Не удалось/);
  await assert.rejects(api.remove(12), /Не удалось/);
});

test('mock supports the same create, list, and idempotent delete operations', async () => {
  const api = createMockNotesApi();
  assert.deepEqual(await api.list(), []);
  const first = await api.add('Первая');
  const second = await api.add('Вторая');
  assert.notEqual(first.id, second.id);
  assert.deepEqual(await api.list(), [first, second]);
  await api.remove(first.id);
  await api.remove(first.id);
  assert.deepEqual(await api.list(), [second]);
});
