import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


folder_id = os.environ.get("YANDEX_FOLDER_ID")
client = OpenAI(
    api_key=os.environ.get("YANDEX_API_KEY"),
    base_url = "https://ai.api.cloud.yandex.net/v1",
    project=folder_id
)

def send_request(prompt):
    response = client.chat.completions.create(
        model=f"gpt://{folder_id}/qwen3.6-35b-a3b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
