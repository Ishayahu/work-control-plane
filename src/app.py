"""Read-only, fixture-backed Bottle/Jinja2 shell (MVP-01, issue #2)."""
from pathlib import Path

from bottle import Bottle, HTTPError, request, response, run, static_file
from jinja2 import Environment, FileSystemLoader, select_autoescape

HERE = Path(__file__).resolve().parent
TEMPLATES = Environment(
    loader=FileSystemLoader(str(HERE / "templates")),
    autoescape=select_autoescape(["html"]),
)

# UI copy, not real task state or a status engine.
VIEWS = {
    "mine": ("Требует моего участия", "Вопросы и действия, ожидающие вашего решения."),
    "ready": ("Можно продолжить", "Задачи, к которым можно вернуться."),
    "ai": ("ИИ может продолжить", "Работа, которую впоследствии сможет продолжить ИИ."),
    "blocked": ("Заблокировано", "Ожидание зависимостей или внешних условий."),
}
app = Bottle()


def demo_messages(value: str) -> list[dict[str, str | int]]:
    """Return bounded fictional examples, never fetch private messages."""
    count = {"0": 0, "3": 3, "20": 20}.get(value, 0)
    examples = (("Письмо о встрече", "E-mail"),
                ("Уточнение по делу", "Telegram"),
                ("Комментарий к проекту", "GitHub"))
    return [
        {"title": examples[i % len(examples)][0],
         "source": examples[i % len(examples)][1], "number": i + 1}
        for i in range(count)
    ]


def render(name: str, **context: object) -> str:
    return TEMPLATES.get_template(name).render(**context)


@app.get("/")
def index() -> str:
    selected = request.query.get("view", "mine")
    if selected not in VIEWS:
        selected = "mine"
    inbox_case = request.query.get("demo_inbox", "0")
    response.content_type = "text/html; charset=UTF-8"
    return render("index.html", views=VIEWS, selected=selected,
                  inbox_case=inbox_case, messages=demo_messages(inbox_case))


@app.get("/task-view/<selected>")
def task_view(selected: str) -> str:
    """Server returns a Jinja2 HTML fragment; HTMX replaces only its target."""
    if selected not in VIEWS:
        raise HTTPError(404, "Unknown demonstration view")
    response.content_type = "text/html; charset=UTF-8"
    return render("_task_switcher.html", views=VIEWS, selected=selected,
                  inbox_case=request.query.get("demo_inbox", "0"))


@app.get("/static/<filename:path>")
def static_asset(filename: str):
    return static_file(filename, root=str(HERE / "static"))


if __name__ == "__main__":
    # Deliberately local only. This fixture-only app has no production auth.
    run(app, host="127.0.0.1", port=8080, debug=True, reloader=False)
