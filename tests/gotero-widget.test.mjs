import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const source = await readFile(new URL('../src/App.jsx', import.meta.url), 'utf8');

test('dashboard renders and refreshes the Gotero queue', () => {
  assert.match(source, /fetch\(['"]\/api\/gotero['"]\)/);
  assert.match(source, /\[ GOTERO QUEUE \]/);
  assert.match(source, /gotero\.pending/);
});
