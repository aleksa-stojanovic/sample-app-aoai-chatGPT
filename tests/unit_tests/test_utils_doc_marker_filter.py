import types
import uuid
import os
import sys

# Ensure project root is on sys.path so 'backend' package can be imported when tests are run directly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend import utils

class DummyDelta:
    def __init__(self, content=None, tool_calls=None, context=None, role="assistant"):
        self.content = content
        self.tool_calls = tool_calls
        self.context = context
        self.role = role

class DummyChoice:
    def __init__(self, delta):
        self.delta = delta

class DummyChunk:
    def __init__(self, delta):
        self.id = str(uuid.uuid4())
        self.model = "gpt-test"
        self.created = 0
        self.object = "chat.completion.chunk"
        self.choices = [DummyChoice(delta)]


def _call(delta_content):
    delta = DummyDelta(content=delta_content)
    chunk = DummyChunk(delta)
    return utils.format_stream_response(chunk, history_metadata={}, apim_request_id="test")


def test_marker_only_chunk_dropped():
    # Chunk that is just markers (and whitespace) should be skipped -> empty dict
    r = _call("[doc1]   [doc23]\n")
    assert r == {}, f"Expected empty dict, got {r}"


def test_chunk_with_markers_and_text_dropped():
    r = _call("This is a test [doc5] with markers [doc10]")
    assert r == {}, f"Expected entire chunk dropped, got {r}"


def test_no_marker_unchanged():
    r = _call("Plain content with no markers.")
    messages = r["choices"][0]["messages"]
    assert messages[0]["content"] == "Plain content with no markers."