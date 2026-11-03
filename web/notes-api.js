export function createNotesApi(fetcher = fetch) {
  async function request(method, path = '/notes', body) {
    const response = await fetcher(path, {
      method,
      ...(body === undefined ? {} : {
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
      }),
    });
    // Another tab may already have deleted the note.
    if (method === 'DELETE' && response.status === 404) return;
    if (!response.ok) throw new Error('Не удалось выполнить запрос. Попробуйте ещё раз.');
    if (response.status !== 204) return response.json();
  }
  return {
    list: () => request('GET'),
    add: text => request('POST', '/notes', { text }),
    remove: id => request('DELETE', `/notes/${id}`),
  };
}

export function createMockNotesApi() {
  let notes = [];
  let nextId = 1;
  return {
    list: async () => notes.map(note => ({ ...note })),
    add: async text => {
      const note = { id: nextId++, text };
      notes.push(note);
      return { ...note };
    },
    remove: async id => { notes = notes.filter(note => note.id !== id); },
  };
}
