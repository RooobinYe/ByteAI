import requests
import json

url = "https://security.bytedance.com/api/challenge/llm/chat"
headers = {"Content-Type": "application/json", "token": "7f126e95da43c08b"}
data = {"chat_req": [{"role": "user", "content": "你好"}]}
response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())
