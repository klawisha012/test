"""Persistent notes HTTP API. Run with python notes_server.py."""

import argparse
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit


def create_server(host, port, database):
    database = str(database)
    with closing(sqlite3.connect(database)) as connection:
        connection.execute(
            'CREATE TABLE IF NOT EXISTS notes '
            '(id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL)'
        )
        connection.commit()

    class Handler(BaseHTTPRequestHandler):
        def respond(self, status, data=None):
            body = json.dumps(data, ensure_ascii=False).encode('utf-8') if data is not None else b''
            self.send_response(status)
            if data is not None:
                self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if urlsplit(self.path).path != '/notes':
                self.respond(404, {'error': 'Not found'})
                return
            with closing(sqlite3.connect(database)) as connection:
                rows = connection.execute('SELECT id, text FROM notes ORDER BY id').fetchall()
            self.respond(200, [{'id': row[0], 'text': row[1]} for row in rows])

        def do_POST(self):
            if urlsplit(self.path).path != '/notes':
                self.respond(404, {'error': 'Not found'})
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 1024 * 1024:
                    raise ValueError('Invalid body length')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError('Expected object')
                text = data.get('text')
                if not isinstance(text, str) or not text.strip():
                    raise ValueError('Expected nonempty text')
            except (ValueError, UnicodeError):
                self.respond(400, {'error': 'Expected JSON with nonempty text'})
                return
            with closing(sqlite3.connect(database)) as connection:
                cursor = connection.execute('INSERT INTO notes (text) VALUES (?)', (text,))
                connection.commit()
                note_id = cursor.lastrowid
            self.respond(201, {'id': note_id, 'text': text})

        def do_DELETE(self):
            match = re.fullmatch(r'/notes/([0-9]+)', urlsplit(self.path).path)
            if match is None or len(match[1]) > 19:
                self.respond(404, {'error': 'Not found'})
                return
            note_id = int(match[1])
            if note_id > 9223372036854775807:
                self.respond(404, {'error': 'Not found'})
                return
            with closing(sqlite3.connect(database)) as connection:
                cursor = connection.execute('DELETE FROM notes WHERE id = ?', (note_id,))
                connection.commit()
                deleted = cursor.rowcount
            if deleted:
                self.respond(204)
            else:
                self.respond(404, {'error': 'Not found'})

    server = ThreadingHTTPServer((host, port), Handler)
    server.timeout = 5
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--database', type=Path, default=Path('notes.sqlite3'))
    args = parser.parse_args()
    server = create_server(args.host, args.port, args.database)
    print(f'Notes API: http://{args.host}:{server.server_port}/notes')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
