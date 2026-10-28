"""Pure-WSGI smoke tests; no real integrations and no data mutations."""
from io import BytesIO
from urllib.parse import urlencode

from app import app, demo_messages


def get(path: str, query: str = "") -> tuple[str, str, dict[str, str]]:
    headers = {}

    def start_response(status, response_headers, exc_info=None):
        headers.update(response_headers)
        headers["status"] = status

    env = {
        "REQUEST_METHOD": "GET", "SCRIPT_NAME": "", "PATH_INFO": path,
        "QUERY_STRING": query, "SERVER_NAME": "localhost", "SERVER_PORT": "80",
        "SERVER_PROTOCOL": "HTTP/1.1", "wsgi.url_scheme": "http",
        "wsgi.version": (1, 0), "wsgi.input": BytesIO(),
        "wsgi.errors": BytesIO(), "wsgi.multithread": False,
        "wsgi.multiprocess": False, "wsgi.run_once": False,
    }
    body = b"".join(app(env, start_response)).decode("utf-8")
    return headers["status"], body, headers


def test_full_page_and_default_empty_inbox():
    status, body, headers = get("/")
    assert status.startswith("200") and "text/html" in headers["Content-Type"]
    assert "<!doctype html>" in body
    assert 'id="task-switcher"' in body
    assert 'class="card inbox"' not in body
    assert "— ₽" in body and "Нет данных" in body
    assert 'hx-target="#task-switcher"' in body
    assert 'id="ai-cost"' in body
    assert "Расходы ИИ" in body and "За текущий месяц" in body
    assert "— ₽" in body  # Unknown spending is not a confirmed zero.



def test_htmx_returns_only_selected_jinja_fragment():
    status, body, _ = get("/task-view/ai")
    assert status.startswith("200")
    assert 'id="task-switcher"' in body and "ИИ может продолжить" in body
    assert 'aria-current="page"' in body
    assert "<!doctype html>" not in body and "<body" not in body


def test_invalid_fragment_is_rejected():
    status, _, _ = get("/task-view/missing")
    assert status.startswith("404")


def test_inbox_examples_are_bounded_and_explicit():
    assert [len(demo_messages(str(n))) for n in (0, 3, 20)] == [0, 3, 20]
    assert len(demo_messages("999999")) == 0
    status, body, _ = get("/", urlencode({"demo_inbox": "20"}))
    assert status.startswith("200")
    assert "20 · демонстрация" in body
    assert body.count('class="message"') == 20
