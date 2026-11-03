import json
import re
from wsgiref.simple_server import make_server

NOTES = {}  # shortcut: in-memory store, lost on restart; swap for a DB when persistence is required
_next_id = 1


def _respond(start_response, status, body=None):
    data = b"" if body is None else json.dumps(body, ensure_ascii=False).encode()
    start_response(status, [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(data)))])
    return [data]


def app(environ, start_response):
    global _next_id
    method, path = environ["REQUEST_METHOD"], environ["PATH_INFO"]
    if path == "/notes" and method == "GET":
        return _respond(start_response, "200 OK", list(NOTES.values()))
    if path == "/notes" and method == "POST":
        try:
            raw = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0))
            text = json.loads(raw)["text"]
        except (ValueError, KeyError, TypeError):
            return _respond(start_response, "400 Bad Request", {"error": "text required"})
        if not isinstance(text, str) or not text.strip():
            return _respond(start_response, "400 Bad Request", {"error": "text required"})
        note = {"id": _next_id, "text": text}
        NOTES[_next_id] = note
        _next_id += 1
        return _respond(start_response, "201 Created", note)
    return _respond(start_response, "404 Not Found", {"error": "not found"})


if __name__ == "__main__":
    make_server("", 8000, app).serve_forever()
