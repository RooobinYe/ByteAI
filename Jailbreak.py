import requests
import json
from transformers import pipeline

pipe = pipeline("text-classification", model="hubert233/GPTFuzz")
file1_path = "Examples/JailbreakExamples.jsonl"
file2_path = "Examples/JailbreakQuestions.txt"
file3_path = "Examples/OneTimeJailbreakExamples.jsonl"  # 便于测试，只包含一条例子
with open(file3_path, "r", encoding="utf-8") as file:
    prompts = []
    for line in file:
        json_obj = json.loads(line.strip())
        prompts.append(json_obj["prompts"])
with open(file2_path, "r", encoding="utf-8") as file:
    questions = file.readlines()
url = "https://security.bytedance.com/api/challenge/llm/chat"
token = "7f126e95da43c08b"
headers = {
    "Content-Type": "application/json",
    "token": token,
}


def replace_prompt(prompts, questions):
    result = []
    for question in questions:
        question = question.strip()
        updated_prompts = []
        for prompt in prompts:
            updated_prompt = {
                "role": prompt["role"],
                "content": prompt["content"].replace("[INSERT_PROMPT_HERE]", question),
            }
            updated_prompts.append(updated_prompt)
        result.append(updated_prompts)
    return result


def count_user_roles(prompts) -> int:
    # 统计 'role' 为 'user' 的条目数量
    user_count = sum(1 for entry in prompts if entry.get("role") == "user")
    return user_count


def get_response(prompts):
    prompts_with_questions = replace_prompt(prompts, questions)
    for prompts_with_question in prompts_with_questions:
        round_count = count_user_roles(prompts_with_question)
        print_prompt_token_cost = []
        print_output_token_cost = []
        for prompt_with_question in prompts_with_question:
            get_response_prompt = (
                []
            )  # 记录了单次对话的所有 prompt，包含 user 和 assistant 的
            get_response_prompt.append(prompt_with_question)  # 添加 user 的 prompt
            data = {"chat_req": get_response_prompt}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("code") == 0:
                    print_prompt_token_cost.append(
                        response_data["data"]["prompt_token_cost"]
                    )
                    print_output_token_cost.append(
                        response_data["data"]["output_token_cost"]
                    )
                    get_response_prompt.append(
                        {
                            "role": "assistant",
                            "content": response_data["data"]["response"],
                        }
                    )
                    print("User: ", end="") # 目的是为了不换行
                    print(prompt_with_question["content"])
                    print("Assistant: ", end="")
                    print(response_data["data"]["response"])
                    print(pipe(response_data["data"]["response"]))
        print_token(print_prompt_token_cost, print_output_token_cost)


def print_token(print_prompt_token_cost, print_output_token_cost):
    all_prompt_token_cost = sum(print_prompt_token_cost)
    all_output_token_cost = sum(print_output_token_cost)
    print(f"Prompt token cost: {all_prompt_token_cost}")
    print(f"Output token cost: {all_output_token_cost}")
    print("\n\n")


def main():
    for prompt in prompts:
        get_response(prompt)


if __name__ == "__main__":
    main()
