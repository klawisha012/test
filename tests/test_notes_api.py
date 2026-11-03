import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from notes_server import create_server


class NotesAPITests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.database = Path(self.directory.name) / 'notes.sqlite3'
        self.start_server()

    def start_server(self):
        self.server = create_server('127.0.0.1', 0, self.database)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def tearDown(self):
        self.stop_server()
        self.directory.cleanup()

    def request(self, method, path='/notes', body=None):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            connection.request(method, path, body, {'Content-Type': 'application/json'})
            response = connection.getresponse()
            data = response.read()
            return response.status, json.loads(data) if data else None
        finally:
            connection.close()

    def test_invalid_text_and_json_are_rejected_without_creating_notes(self):
        for body in ['{}', '{"text":""}', '{"text":"  "}', '{"text":null}',
                     '{"text":42}', '[]', 'null', '{']:
            with self.subTest(body=body):
                self.assertEqual(self.request('POST', body=body)[0], 400)
        self.assertEqual(self.request('GET'), (200, []))

    def test_delete_is_persistent_and_unknown_id_returns_404(self):
        _, first = self.request('POST', body='{"text":"first"}')
        _, second = self.request('POST', body='{"text":"second"}')
        path = f'/notes/{first["id"]}'
        self.assertEqual(self.request('DELETE', path), (204, None))
        self.assertEqual(self.request('DELETE', path)[0], 404)
        self.assertEqual(self.request('GET'), (200, [second]))
        self.stop_server()
        self.start_server()
        self.assertEqual(self.request('GET'), (200, [second]))
        self.assertEqual(self.request('DELETE', '/notes/999999')[0], 404)

    def test_create_and_list_notes_survive_server_restart(self):
        self.assertEqual(self.request('GET'), (200, []))
        status, note = self.request('POST', body=json.dumps({'text': 'Первая заметка'}))
        self.assertEqual(status, 201)
        self.assertIs(type(note['id']), int)
        self.assertEqual(note['text'], 'Первая заметка')
        self.assertEqual(self.request('GET'), (200, [note]))
        self.stop_server()
        self.start_server()
        self.assertEqual(self.request('GET'), (200, [note]))


if __name__ == '__main__':
    unittest.main()
