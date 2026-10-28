import json
from pathlib import Path
from string import Template
import connectors.yandex_ai
from connectors import yandex_ai

MATRIX_FILE = Path(__file__).parent / "model_matrix.json"

def choose_model(request):
    matrix = __get_matrix()
    matrix_as_text = json.dumps(matrix, ensure_ascii=False)
    DISPATCHER_REQUEST_FILE = Path(__file__).parent.parent / "criteria" / "dispatcher.md"
    with open(DISPATCHER_REQUEST_FILE, "r", encoding="utf-8") as file:
        dispatcher_request = file.read()
    dispatcher_request = Template(dispatcher_request).substitute(matrix_json=matrix_as_text, request=request)
    answer = yandex_ai.send_request(dispatcher_request)
    response = json.loads(answer)
    candidates = []
    for candidate in response["candidates"]:
        candidate_model = candidate["model"]
        candidate_effort = candidate["effort"]
        candidate_cost = matrix["models"][candidate_model]["efforts"][candidate_effort]["expected_cost"]
        candidates.append((candidate_model, candidate_effort, candidate_cost))
    candidates.sort(key=lambda x: x[2])
    print(candidates)


def __update_matrix():
    pass

def __get_matrix():
    with open(MATRIX_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    # matrix = __get_matrix()
    # print(matrix["version"])
    # print(matrix["models"])
    choose_model("МОЙ ЗАПРОС ОЧЕНЬ ЛЁГКИЙ. Любая модель с ним справится")
