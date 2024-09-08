import requests
import json

# 读取两个文件的内容
file1_path = "Examples/JailbreakExamples.txt"
file2_path = "Examples/JailbreakQuestions.txt"

with open(file1_path, "r", encoding="utf-8") as file:
    examples = file.readlines()

with open(file2_path, "r", encoding="utf-8") as file:
    questions = file.readlines()

url = "https://security.bytedance.com/api/challenge/llm/chat"
token = "7f126e95da43c08b"  # 请替换为你的实际 token
headers = {
    "Content-Type": "application/json",
    "token": token,
}

# 针对每行发送一个请求
for example_line in examples:
    example_content = example_line.strip()
    if not example_content:  # 跳过空行
        continue

    # 如果包含 [INSERT_PROMPT_HERE]，替换并发送十个请求
    if "[INSERT_PROMPT_HERE]" in example_content:
        for question in questions[:10]:  # 假设我们只用前十个问题
            question_content = question.strip()
            filled_content = example_content.replace(
                "[INSERT_PROMPT_HERE]", question_content
            )

            data = {"chat_req": [{"role": "user", "content": filled_content}]}
            response = requests.post(url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("code") == 0:
                    chat_response = response_data["data"]["response"]
                    prompt_token_cost = response_data["data"]["prompt_token_cost"]
                    output_token_cost = response_data["data"]["output_token_cost"]

                    print(f"Content: {filled_content}")
                    print(f"Response: {chat_response}")
                    print(f"Prompt Token Cost: {prompt_token_cost}")
                    print(f"Output Token Cost: {output_token_cost}\n")
                else:
                    print("Error with code:", response_data.get("code"))
            else:
                print("Request failed with status code:", response.status_code)