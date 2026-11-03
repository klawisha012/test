import { createNotesApi, createMockNotesApi } from './notes-api.js';

const api = new URLSearchParams(location.search).get('mock') === '1'
  ? createMockNotesApi() : createNotesApi();
const form = document.querySelector('#note-form');
const input = document.querySelector('#text');
const add = document.querySelector('#add');
const list = document.querySelector('#notes');
const count = document.querySelector('#count');
const status = document.querySelector('#status');
let notes = [];
let saving = false;

function render() {
  count.textContent = notes.length;
  list.replaceChildren();
  for (const note of notes) {
    const item = document.createElement('li');
    const text = document.createElement('p');
    text.textContent = note.text;
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.textContent = 'Удалить';
    remove.setAttribute('aria-label', `Удалить заметку: ${note.text}`);
    remove.addEventListener('click', async () => {
      remove.disabled = true;
      try {
        await api.remove(note.id);
        notes = notes.filter(value => value.id !== note.id);
        render();
      } catch (error) {
        status.textContent = error.message;
        remove.disabled = false;
      }
    });
    item.append(text, remove);
    list.append(item);
  }
  status.textContent = notes.length ? '' : 'Здесь появятся ваши заметки. Начните с первой мысли.';
}

input.addEventListener('input', () => { add.disabled = saving || !input.value.trim(); });
form.addEventListener('submit', async event => {
  event.preventDefault();
  if (saving || !input.value.trim()) return;
  saving = true;
  add.disabled = true;
  input.disabled = true;
  try {
    notes.push(await api.add(input.value));
    input.value = '';
    render();
  } catch (error) {
    status.textContent = error.message;
  } finally {
    saving = false;
    input.disabled = false;
    add.disabled = !input.value.trim();
    input.focus();
  }
});

try {
  notes = await api.list();
  render();
  input.disabled = false;
} catch (error) {
  status.textContent = error.message;
}
