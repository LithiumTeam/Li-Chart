
from openai import OpenAI
import json

with open("./assets/data.json", "r") as file:
    config = json.load(file)

client = OpenAI(
    api_key=config["env.api.key"],
    base_url=config["env.base.api.url"],
    timeout=30
)

try:
    response = client.chat.completions.create(
        model="agnes-2.5-flash",
        messages=[
            {"role": "user", "content": "Hello! Reply with OK."}
        ]
    )

    print(response.choices[0].message.content)

except Exception as e:
    print("Error Type:", type(e).__name__)
    print("Error Message:", str(e))
