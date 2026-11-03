import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
import notes


def call(method, path, body=None):
    raw = json.dumps(body).encode() if body is not None else b""
    status = []
    env = {"REQUEST_METHOD": method, "PATH_INFO": path, "CONTENT_LENGTH": str(len(raw)), "wsgi.input": io.BytesIO(raw)}
    out = b"".join(notes.app(env, lambda s, h: status.append(s)))
    return int(status[0][:3]), json.loads(out) if out else None


class NotesTest(unittest.TestCase):
    def setUp(self):
        notes.NOTES.clear()

    def test_create_and_list(self):
        code, note = call("POST", "/notes", {"text": "купить хлеб"})
        self.assertEqual((code, note["text"]), (201, "купить хлеб"))
        self.assertEqual(call("GET", "/notes"), (200, [note]))

    def test_empty_text_rejected(self):
        for body in ({"text": ""}, {"text": "   "}, {}, {"text": 5}):
            self.assertEqual(call("POST", "/notes", body)[0], 400)
        self.assertEqual(call("GET", "/notes"), (200, []))

    def test_delete(self):
        _, note = call("POST", "/notes", {"text": "x"})
        self.assertEqual(call("DELETE", f"/notes/{note['id']}"), (204, None))
        self.assertEqual(call("GET", "/notes"), (200, []))

    def test_delete_unknown_id(self):
        self.assertEqual(call("DELETE", "/notes/999")[0], 404)


if __name__ == "__main__":
    unittest.main()
